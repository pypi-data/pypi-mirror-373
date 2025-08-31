use ::twinleaf::tio::*;
use ::twinleaf::*;
use pyo3::exceptions::PyRuntimeError;
use pyo3::prelude::*;
use pyo3::types::{PyBytes, PyDict};

#[pyclass(name = "DataIterator", subclass)]
struct PyIter {
    port: data::Device,
    n: Option<usize>,
    stream: String,
    columns: Vec<String>,
}

#[pymethods]
impl PyIter {
    fn __iter__(slf: PyRef<'_, Self>) -> PyRef<'_, Self> {
        slf
    }

    fn __next__(mut slf: PyRefMut<'_, Self>) -> PyResult<Option<Py<PyAny>>> {
        let dict = PyDict::new(slf.py());

        if let Some(ctr) = slf.n {
            if ctr == 0 {
                // TODO: drop port
                return Ok(None);
            } else {
                slf.n = Some(ctr - 1);
            }
        }

        while dict.is_empty() {
            // Check for keyboard interrupt
            slf.py().check_signals()?;

            let sample = match slf.port.next() {
                Ok(sample) => sample,
                Err(_) => return Ok(None), // End of stream or error
            };
            if !slf.stream.is_empty() && slf.stream != sample.stream.name {
                continue;
            }

            for sample_column in &sample.columns {
                let sample_column_name = sample_column.desc.name.clone();
                let column_matches = slf.columns.is_empty() || slf.columns.iter().any(|c| {
                    if c.ends_with("*") {
                        // Remove * and check if sample_column_name starts with prefix
                        let prefix = &c[..c.len()-1];
                        sample_column_name.starts_with(prefix)
                    } else {
                        c.eq(&sample_column_name)
                    }
                });
                if column_matches {
                    let time = sample.timestamp_end().into_pyobject(slf.py())?;
                    let stream_id = sample.stream.stream_id.into_pyobject(slf.py())?;
                    dict.set_item("stream", stream_id)?;
                    dict.set_item("time", time)?;
                    match sample_column.value {
                        data::ColumnData::Int(x) => {
                            dict.set_item(sample_column_name.into_pyobject(slf.py())?, x.into_pyobject(slf.py())?)?
                        }
                        data::ColumnData::UInt(x) => {
                            dict.set_item(sample_column_name.into_pyobject(slf.py())?, x.into_pyobject(slf.py())?)?
                        }
                        data::ColumnData::Float(x) => {
                            dict.set_item(sample_column_name.into_pyobject(slf.py())?, x.into_pyobject(slf.py())?)?
                        }
                        _ => dict.set_item(sample_column_name.into_pyobject(slf.py())?, "UNKNOWN".into_pyobject(slf.py())?)?,
                    };
                }
            }
        }

        Ok(Some(dict.into()))
    }
}

#[pyclass(name = "Device", subclass)]
struct PyDevice {
    proxy: proxy::Interface,
    route: proto::DeviceRoute,
    rpc: proxy::Port,
}

#[pymethods]
impl PyDevice {
    #[new]
    #[pyo3(signature = (root_url=None, route=None))]
    fn new(root_url: Option<String>, route: Option<String>) -> PyResult<PyDevice> {
        let root = if let Some(url) = root_url {
            url
        } else {
            "tcp://localhost".to_string()
        };
        let route = if let Some(path) = route {
            proto::DeviceRoute::from_str(&path).unwrap()
        } else {
            proto::DeviceRoute::root()
        };
        let proxy = proxy::Interface::new(&root);
        let rpc = proxy.device_rpc(route.clone()).unwrap();
        Ok(PyDevice { proxy, route, rpc })
    }

    fn _rpc<'py>(&self, py: Python<'py>, name: &str, req: &[u8]) -> PyResult<Bound<'py, PyBytes>> {
        match self.rpc.raw_rpc(name, req) {
            Ok(ret) => Ok(PyBytes::new(py, &ret[..])),
            _ => Err(PyRuntimeError::new_err(format!("RPC '{}' failed", name))),
        }
    }

    #[pyo3(signature = (n=1, stream=None, columns=None))]
    fn _samples<'py>(
        &self,
        _py: Python<'py>,
        n: Option<usize>,
        stream: Option<String>,
        columns: Option<Vec<String>>,
    ) -> PyResult<PyIter> {
        Ok(PyIter {
            port: data::Device::new(self.proxy.device_full(self.route.clone()).unwrap()),
            n: n,
            stream: stream.unwrap_or_default(),
            columns: columns.unwrap_or_default(),
        })
    }

    fn _get_metadata<'py>(&self, py: Python<'py>) -> PyResult<Py<PyAny>> {
        let mut device = data::Device::new(self.proxy.device_full(self.route.clone()).unwrap());
        let meta = match device.get_metadata() {
            Ok(meta) => meta,
            Err(_) => return Err(PyRuntimeError::new_err("Failed to get metadata")),
        };

        let dict = PyDict::new(py);

        // Convert device metadata to dict
        let device_dict = PyDict::new(py);
        device_dict.set_item("serial_number", meta.device.serial_number.to_string())?;
        device_dict.set_item("firmware_hash", meta.device.firmware_hash.to_string())?;
        device_dict.set_item("session_id", meta.device.session_id.to_string())?;
        device_dict.set_item("name", meta.device.name.to_string())?;
        dict.set_item("device", device_dict)?;

        // Convert streams to dict
        let streams_dict = PyDict::new(py);
        for (_, stream) in meta.streams {
            let stream_dict = PyDict::new(py);
            stream_dict.set_item("stream_id", stream.stream.stream_id.to_string())?;
            // stream_dict.set_item("name", stream.name.to_string())?;

            let columns_dict = PyDict::new(py);
            for col in stream.columns {
                let col_dict = PyDict::new(py);
                col_dict.set_item("name", col.name.to_string())?;
                col_dict.set_item("description", col.description.to_string())?;
                col_dict.set_item("type", format!("{:?}", col.data_type))?;
                col_dict.set_item("units", col.units.to_string())?;

                columns_dict.set_item(col.name.to_string(), col_dict)?;
            }
            stream_dict.set_item("columns", columns_dict)?;
            streams_dict.set_item(stream.stream.name.to_string(), stream_dict)?;
        }
        dict.set_item("streams", streams_dict)?;

        Ok(dict.into())
    }
}

/// A Python module implemented in Rust. The name of this function must match
/// the `lib.name` setting in the `Cargo.toml`, else Python will not be able to
/// import the module.
#[pymodule]
fn _twinleaf(_py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyDevice>()?;
    Ok(())
}

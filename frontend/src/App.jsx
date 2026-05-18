import {
  AlertTriangle,
  BarChart3,
  CheckCircle2,
  Database,
  Filter,
  LineChart,
  RefreshCw,
  Save,
  Search,
  Upload
} from 'lucide-react';
import { useEffect, useMemo, useState } from 'react';

const API = import.meta.env.VITE_API_BASE || '';

const emptyDraft = {
  id: '',
  manufacturer: '',
  part_number: '',
  technology: 'SiC',
  device_class: 'mosfet',
  tags: [],
  package: { name: '', mounting: '', pins: [] },
  ratings: {
    voltage: { value: 0, unit: 'V', condition: {}, source_id: 'ds' },
    current: { value: 0, unit: 'A', condition: {}, source_id: 'ds' }
  },
  sources: [{ id: 'ds', type: 'datasheet', title: '' }]
};

export function App() {
  const [devices, setDevices] = useState([]);
  const [taxonomy, setTaxonomy] = useState(null);
  const [selectedId, setSelectedId] = useState(null);
  const [detail, setDetail] = useState(null);
  const [query, setQuery] = useState('');
  const [manufacturer, setManufacturer] = useState('');
  const [technology, setTechnology] = useState('');
  const [deviceClass, setDeviceClass] = useState('');
  const [activeTab, setActiveTab] = useState('overview');
  const [editorText, setEditorText] = useState(JSON.stringify(emptyDraft, null, 2));
  const [csvText, setCsvText] = useState('0,0\n1,2\n2,4');
  const [curvePreview, setCurvePreview] = useState(null);
  const [status, setStatus] = useState('');

  useEffect(() => {
    loadTaxonomy();
    loadDevices();
  }, []);

  useEffect(() => {
    loadDevices();
  }, [query, manufacturer, technology, deviceClass]);

  useEffect(() => {
    if (selectedId) {
      loadDevice(selectedId);
    }
  }, [selectedId]);

  async function loadTaxonomy() {
    const response = await fetch(`${API}/api/taxonomy`);
    setTaxonomy(await response.json());
  }

  async function loadDevices() {
    const params = new URLSearchParams();
    if (query) params.set('q', query);
    if (manufacturer) params.set('manufacturer', manufacturer);
    if (technology) params.set('technology', technology);
    if (deviceClass) params.set('device_class', deviceClass);
    const response = await fetch(`${API}/api/devices?${params}`);
    const rows = await response.json();
    setDevices(rows);
    if (!selectedId && rows.length) setSelectedId(rows[0].id);
  }

  async function loadDevice(id) {
    const response = await fetch(`${API}/api/devices/${id}`);
    const payload = await response.json();
    setDetail(payload);
    setEditorText(JSON.stringify(payload.device, null, 2));
  }

  async function rebuildIndex() {
    const response = await fetch(`${API}/api/index/rebuild`, { method: 'POST' });
    const payload = await response.json();
    setStatus(`Indexed ${payload.indexed} devices`);
    await loadDevices();
  }

  async function validateDraft() {
    const record = JSON.parse(editorText);
    const response = await fetch(`${API}/api/devices/validate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(record)
    });
    const validation = await response.json();
    setDetail((current) => ({ ...(current || {}), device: record, validation }));
    setStatus(validation.errors.length ? 'Validation failed' : 'Validation passed');
  }

  async function saveDraft() {
    const record = JSON.parse(editorText);
    const method = record.id && devices.some((device) => device.id === record.id) ? 'PUT' : 'POST';
    const url = method === 'PUT' ? `${API}/api/devices/${record.id}` : `${API}/api/devices`;
    const response = await fetch(url, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(record)
    });
    if (!response.ok) {
      const error = await response.json();
      setStatus(`Save failed: ${JSON.stringify(error.detail)}`);
      return;
    }
    const payload = await response.json();
    setStatus(`Saved ${payload.device.id}`);
    setSelectedId(payload.device.id);
    await loadDevices();
  }

  async function previewCurveImport() {
    const sourceId = detail?.device?.sources?.[0]?.id || 'ds';
    const response = await fetch(`${API}/api/curves/import-csv`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        csv_text: csvText,
        curve_id: 'imported-curve',
        curve_type: 'iv_output',
        x_label: 'Voltage',
        x_unit: 'V',
        y_label: 'Current',
        y_unit: 'A',
        source_id: sourceId,
        condition: { imported_from_ui: true }
      })
    });
    setCurvePreview(await response.json());
  }

  const comparisonRows = useMemo(() => devices.slice(0, 6), [devices]);
  const validation = detail?.validation || { errors: [], warnings: [] };
  const selectedDevice = detail?.device;

  return (
    <main className="app-shell">
      <aside className="sidebar">
        <div className="brand-row">
          <Database size={20} />
          <div>
            <h1>AIPE Device Library</h1>
            <span>{devices.length} indexed devices</span>
          </div>
        </div>

        <div className="search-row">
          <Search size={16} />
          <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search part, maker, tag" />
        </div>

        <div className="filter-grid">
          <label>
            <Database size={14} />
            <select value={manufacturer} onChange={(event) => setManufacturer(event.target.value)}>
              <option value="">All makers</option>
              {(taxonomy?.manufacturers || []).map((item) => (
                <option key={item} value={item}>{item}</option>
              ))}
            </select>
          </label>
          <label>
            <Filter size={14} />
            <select value={technology} onChange={(event) => setTechnology(event.target.value)}>
              <option value="">All tech</option>
              {(taxonomy?.technologies || []).map((item) => (
                <option key={item} value={item}>{item}</option>
              ))}
            </select>
          </label>
          <label>
            <BarChart3 size={14} />
            <select value={deviceClass} onChange={(event) => setDeviceClass(event.target.value)}>
              <option value="">All classes</option>
              {(taxonomy?.device_classes || []).map((item) => (
                <option key={item} value={item}>{item}</option>
              ))}
            </select>
          </label>
        </div>

        <button className="icon-button" onClick={rebuildIndex} title="Rebuild SQLite index">
          <RefreshCw size={16} />
          Rebuild index
        </button>

        <div className="device-list">
          {devices.map((device) => (
            <button
              key={device.id}
              className={device.id === selectedId ? 'device-row selected' : 'device-row'}
              onClick={() => setSelectedId(device.id)}
            >
              <strong>{device.part_number}</strong>
              <span>{device.manufacturer} · {device.technology} {device.device_class}</span>
              <small>{device.voltage_v || '-'} V · {device.current_a || '-'} A · {device.package_name}</small>
            </button>
          ))}
        </div>
      </aside>

      <section className="workspace">
        <header className="topbar">
          <div>
            <h2>{selectedDevice?.part_number || 'New device'}</h2>
            <p>{selectedDevice?.manufacturer || 'Create or select a device record'}</p>
          </div>
          <div className="status-line">
            {validation.errors.length ? <AlertTriangle size={18} /> : <CheckCircle2 size={18} />}
            <span>{validation.errors.length} errors · {validation.warnings.length} warnings</span>
          </div>
        </header>

        <nav className="tabs">
          {['overview', 'electrical', 'curves', 'thermal', 'package', 'sources', 'validation', 'compare', 'editor'].map((tab) => (
            <button key={tab} className={activeTab === tab ? 'active' : ''} onClick={() => setActiveTab(tab)}>
              {tab}
            </button>
          ))}
        </nav>

        <section className="panel-area">
          {activeTab === 'overview' && <Overview device={selectedDevice} />}
          {activeTab === 'electrical' && <QuantityTable title="Electrical" data={selectedDevice?.electrical} />}
          {activeTab === 'curves' && (
            <Curves curves={selectedDevice?.curves || []} csvText={csvText} setCsvText={setCsvText} previewCurveImport={previewCurveImport} preview={curvePreview} />
          )}
          {activeTab === 'thermal' && <QuantityTable title="Thermal" data={selectedDevice?.thermal} />}
          {activeTab === 'package' && <PackageView device={selectedDevice} />}
          {activeTab === 'sources' && <Sources device={selectedDevice} />}
          {activeTab === 'validation' && <Validation validation={validation} />}
          {activeTab === 'compare' && <Compare rows={comparisonRows} />}
          {activeTab === 'editor' && (
            <Editor editorText={editorText} setEditorText={setEditorText} validateDraft={validateDraft} saveDraft={saveDraft} status={status} />
          )}
        </section>
      </section>
    </main>
  );
}

function Overview({ device }) {
  if (!device) return <EmptyState />;
  return (
    <div className="overview-grid">
      <Info label="Technology" value={device.technology} />
      <Info label="Class" value={device.device_class} />
      <Info label="Package" value={device.package?.name} />
      <Info label="Voltage" value={formatQuantity(device.ratings?.voltage)} />
      <Info label="Current" value={formatQuantity(device.ratings?.current)} />
      <Info label="Tags" value={(device.tags || []).join(', ')} />
      {device.gan && <Info label="GaN structure" value={device.gan.structure} />}
      {device.module && <Info label="Module topology" value={device.module.topology} />}
      <article className="wide-note">{device.description}</article>
    </div>
  );
}

function QuantityTable({ title, data }) {
  return (
    <div>
      <h3>{title}</h3>
      <table>
        <thead>
          <tr><th>Parameter</th><th>Value</th><th>Condition</th><th>Source</th></tr>
        </thead>
        <tbody>
          {Object.entries(data || {}).map(([key, item]) => (
            <tr key={key}>
              <td>{key}</td>
              <td>{formatQuantity(item)}</td>
              <td>{formatCondition(item.condition)}</td>
              <td>{item.source_id}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function Curves({ curves, csvText, setCsvText, previewCurveImport, preview }) {
  return (
    <div className="split">
      <div>
        <h3>Curves</h3>
        {curves.map((curve) => (
          <article className="curve-item" key={curve.id}>
            <div>
              <strong>{curve.id}</strong>
              <span>{curve.type} · {curve.points?.length || 0} points</span>
            </div>
            <MiniCurve points={curve.points || []} />
          </article>
        ))}
      </div>
      <div>
        <h3>CSV import preview</h3>
        <textarea value={csvText} onChange={(event) => setCsvText(event.target.value)} />
        <button className="icon-button" onClick={previewCurveImport} title="Preview CSV curve">
          <Upload size={16} />
          Preview curve
        </button>
        {preview && <pre>{JSON.stringify(preview, null, 2)}</pre>}
      </div>
    </div>
  );
}

function MiniCurve({ points }) {
  if (!points.length) return null;
  const xs = points.map((point) => point[0]);
  const ys = points.map((point) => point[1]);
  const minX = Math.min(...xs);
  const maxX = Math.max(...xs);
  const minY = Math.min(...ys);
  const maxY = Math.max(...ys);
  const path = points
    .map((point, index) => {
      const x = maxX === minX ? 0 : ((point[0] - minX) / (maxX - minX)) * 150;
      const y = maxY === minY ? 30 : 60 - ((point[1] - minY) / (maxY - minY)) * 50;
      return `${index === 0 ? 'M' : 'L'} ${x.toFixed(1)} ${y.toFixed(1)}`;
    })
    .join(' ');
  return (
    <svg className="mini-curve" viewBox="0 0 150 70" aria-label="curve preview">
      <path d={path} />
    </svg>
  );
}

function PackageView({ device }) {
  if (!device) return <EmptyState />;
  return (
    <div className="overview-grid">
      <Info label="Name" value={device.package?.name} />
      <Info label="Mounting" value={device.package?.mounting} />
      <Info label="Pins" value={(device.package?.pins || []).join(', ')} />
      {device.module && <Info label="Switch positions" value={(device.module.switch_positions || []).join(', ')} />}
      {device.module && <Info label="Has NTC" value={String(device.module.has_ntc)} />}
    </div>
  );
}

function Sources({ device }) {
  const sources = device?.sources || [];
  const rawDataPackages = device?.raw_data_packages || [];
  return (
    <div className="split">
      <div>
        <h3>Sources</h3>
        <div className="source-list">
          {sources.map((source) => (
            <article key={source.id}>
              <strong>{source.id} · {source.type}</strong>
              <span>{source.title}</span>
              <small>{source.category || '-'} · {source.subtype || '-'} · {source.lab || source.revision || source.date || ''}</small>
            </article>
          ))}
        </div>
      </div>
      <div>
        <h3>Raw data packages</h3>
        <div className="source-list">
          {rawDataPackages.map((item) => (
            <article key={item.id}>
              <strong>{item.id}</strong>
              <span>{item.test_type} · source {item.source_id}</span>
              <small>{item.test_date || '-'} · {(item.artifacts || []).length} artifacts</small>
            </article>
          ))}
          {!rawDataPackages.length && <article>No raw test data linked yet.</article>}
        </div>
      </div>
    </div>
  );
}

function Validation({ validation }) {
  return (
    <div className="validation-grid">
      <section>
        <h3>Errors</h3>
        {(validation.errors || []).map((item) => <p className="issue error" key={item}>{item}</p>)}
      </section>
      <section>
        <h3>Warnings</h3>
        {(validation.warnings || []).map((item) => <p className="issue warning" key={item}>{item}</p>)}
      </section>
    </div>
  );
}

function Compare({ rows }) {
  return (
    <div>
      <h3>Comparison</h3>
      <table>
        <thead>
          <tr><th>Part</th><th>Maker</th><th>Technology</th><th>Class</th><th>Voltage</th><th>Current</th><th>Package</th></tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={row.id}>
              <td>{row.part_number}</td>
              <td>{row.manufacturer}</td>
              <td>{row.technology}</td>
              <td>{row.device_class}</td>
              <td>{row.voltage_v}</td>
              <td>{row.current_a}</td>
              <td>{row.package_name}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function Editor({ editorText, setEditorText, validateDraft, saveDraft, status }) {
  return (
    <div>
      <div className="editor-actions">
        <button className="icon-button" onClick={validateDraft} title="Validate JSON">
          <CheckCircle2 size={16} />
          Validate
        </button>
        <button className="icon-button" onClick={saveDraft} title="Save device">
          <Save size={16} />
          Save
        </button>
        <span>{status}</span>
      </div>
      <textarea className="json-editor" value={editorText} onChange={(event) => setEditorText(event.target.value)} />
    </div>
  );
}

function Info({ label, value }) {
  return (
    <article className="info-tile">
      <span>{label}</span>
      <strong>{value || '-'}</strong>
    </article>
  );
}

function EmptyState() {
  return (
    <div className="empty-state">
      <LineChart size={28} />
      <span>No device selected</span>
    </div>
  );
}

function formatQuantity(quantity) {
  if (!quantity) return '-';
  return `${quantity.value} ${quantity.unit}`;
}

function formatCondition(condition) {
  if (!condition) return '-';
  return Object.entries(condition).map(([key, value]) => `${key}: ${value}`).join(', ');
}

import React, { useState, useEffect, useCallback } from "react";
import { Plus, Trash2, Pencil, X, Check } from "lucide-react";

/* 
  API Base URL
  Empty string because frontend is served from the same origin as the API in production.
*/
const API_BASE = "";

/* Available colors for note cards */
const NOTE_COLORS = [
  "#fff9c4", "#c8e6c9", "#bbdefb", "#f8bbd0", "#d1c4e9", "#ffe0b2", "#b2dfdb", "#ffccbc",
];

export default function App() {
  /* Board Data States */
  const [columns, setColumns] = useState([]);
  const [notes, setNotes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  /* Modal & Form States */
  const [modal, setModal] = useState({ type: null, columnId: null, note: null, column: null });
  const [formTitle, setFormTitle] = useState("");
  const [formContent, setFormContent] = useState("");
  const [formColor, setFormColor] = useState(NOTE_COLORS[0]);

  /* Drag & Drop States */
  const [draggedNote, setDraggedNote] = useState(null);
  const [dragOverColumn, setDragOverColumn] = useState(null);

  /* Fetch all data from the backend */
  const fetchData = useCallback(async () => {
    try {
      setError(null);
      const [colRes, noteRes] = await Promise.all([
        fetch(`${API_BASE}/api/columns`),
        fetch(`${API_BASE}/api/notes`),
      ]);
      if (!colRes.ok || !noteRes.ok) throw new Error("Failed to load data");
      setColumns(await colRes.json());
      setNotes(await noteRes.json());
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchData(); }, [fetchData]);

  /* Column CRUD Operations */
  const handleColumnSubmit = async () => {
    if (!formTitle.trim()) return;
    try {
      const url = modal.type === "editColumn" ? `${API_BASE}/api/columns/${modal.column._id}` : `${API_BASE}/api/columns`;
      const method = modal.type === "editColumn" ? "PUT" : "POST";
      const res = await fetch(url, {
        method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title: formTitle }),
      });
      if (!res.ok) throw new Error("Failed to save column");
      await fetchData();
      closeModal();
    } catch (err) { setError(err.message); }
  };

  const deleteColumn = async (id) => {
    if (!window.confirm("Delete column and all its notes?")) return;
    try {
      await fetch(`${API_BASE}/api/columns/${id}`, { method: "DELETE" });
      await fetchData();
    } catch (err) { setError(err.message); }
  };

  /* Note CRUD Operations */
  const handleNoteSubmit = async () => {
    if (!formTitle.trim()) return;
    try {
      const url = modal.type === "editNote" ? `${API_BASE}/api/notes/${modal.note._id}` : `${API_BASE}/api/notes`;
      const method = modal.type === "editNote" ? "PUT" : "POST";
      const body = modal.type === "editNote" 
        ? { title: formTitle, content: formContent, color: formColor }
        : { title: formTitle, content: formContent, column_id: modal.columnId, color: formColor };
      
      const res = await fetch(url, {
        method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      if (!res.ok) throw new Error("Failed to save note");
      await fetchData();
      closeModal();
    } catch (err) { setError(err.message); }
  };

  const deleteNote = async (id) => {
    try {
      await fetch(`${API_BASE}/api/notes/${id}`, { method: "DELETE" });
      await fetchData();
    } catch (err) { setError(err.message); }
  };

  const moveNote = async (noteId, targetColumnId) => {
    try {
      const count = notes.filter(n => n.column_id === targetColumnId).length;
      await fetch(`${API_BASE}/api/notes/${noteId}/move`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ column_id: targetColumnId, order: count }),
      });
      await fetchData();
    } catch (err) { setError(err.message); }
  };

  /* Modal Logic */
  const closeModal = () => {
    setModal({ type: null, columnId: null, note: null, column: null });
    setFormTitle(""); setFormContent("");
  };

  const openNoteModal = (note = null, columnId = null) => {
    setModal({ type: note ? "editNote" : "addNote", columnId, note, column: null });
    setFormTitle(note?.title || "");
    setFormContent(note?.content || "");
    setFormColor(note?.color || NOTE_COLORS[0]);
  };

  const openColumnModal = (column = null) => {
    setModal({ type: column ? "editColumn" : "addColumn", columnId: null, note: null, column });
    setFormTitle(column?.title || "");
  };

  if (loading) return <div className="flex items-center justify-center h-screen text-gray-400">Loading Board...</div>;

  return (
    <div className="p-8 min-h-screen">
      <header className="text-center mb-10">
        <h1 className="text-4xl font-bold text-[#e94560] tracking-wider mb-2">KANBAN NOTES</h1>
        <p className="text-gray-500">Organize your thoughts with ease</p>
      </header>

      {error && (
        <div className="bg-red-900/20 text-red-500 p-4 rounded-lg mb-6 flex justify-between items-center max-w-2xl mx-auto">
          <span>Error: {error}</span>
          <button onClick={() => setError(null)}><X size={20} /></button>
        </div>
      )}

      <div className="flex gap-6 overflow-x-auto pb-6 items-start">
        {columns.map(col => (
          <div 
            key={col._id} 
            className={`bg-[#16213e] rounded-xl p-4 w-80 shrink-0 shadow-xl border-t-4 border-[#e94560] ${dragOverColumn === col._id ? 'ring-2 ring-[#e94560]/50 bg-[#1a2a4a]' : ''}`}
            onDragOver={(e) => { e.preventDefault(); setDragOverColumn(col._id); }}
            onDragLeave={() => setDragOverColumn(null)}
            onDrop={(e) => { e.preventDefault(); setDragOverColumn(null); if (draggedNote) moveNote(draggedNote._id, col._id); }}
          >
            <div className="flex justify-between items-center mb-4 pb-2 border-b border-[#0f3460]">
              <h2 className="font-bold text-lg text-[#e94560] truncate pr-2">{col.title}</h2>
              <div className="flex gap-1">
                <button onClick={() => openColumnModal(col)} className="p-1 hover:text-[#e94560] text-gray-500 transition-colors"><Pencil size={16} /></button>
                <button onClick={() => deleteColumn(col._id)} className="p-1 hover:text-red-500 text-gray-500 transition-colors"><Trash2 size={16} /></button>
              </div>
            </div>

            <div className="space-y-3 min-h-[50px]">
              {notes.filter(n => n.column_id === col._id).sort((a, b) => a.order - b.order).map(note => (
                <div 
                  key={note._id}
                  draggable
                  onDragStart={() => setDraggedNote(note)}
                  onDragEnd={() => setDraggedNote(null)}
                  className="p-4 rounded-lg shadow-md cursor-grab active:cursor-grabbing relative group transition-transform hover:-translate-y-1"
                  style={{ backgroundColor: note.color || '#fff9c4' }}
                >
                  <div className="absolute top-2 right-2 flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button onClick={() => openNoteModal(note)} className="p-1 bg-black/10 hover:bg-black/20 rounded text-gray-700"><Pencil size={14} /></button>
                    <button onClick={() => deleteNote(note._id)} className="p-1 bg-black/10 hover:bg-black/20 rounded text-gray-700"><X size={14} /></button>
                  </div>
                  <h3 className="font-bold text-gray-900 mb-1 pr-12">{note.title}</h3>
                  <p className="text-gray-700 text-sm whitespace-pre-wrap">{note.content}</p>
                </div>
              ))}
            </div>

            <button 
              onClick={() => openNoteModal(null, col._id)}
              className="w-full mt-4 py-2 border-2 border-dashed border-[#e94560]/30 rounded-lg text-[#e94560] hover:bg-[#e94560]/10 transition-colors flex items-center justify-center gap-2"
            >
              <Plus size={18} /> Add Note
            </button>
          </div>
        ))}

        <button 
          onClick={() => openColumnModal()}
          className="bg-[#16213e]/50 border-2 border-dashed border-[#e94560]/30 rounded-xl p-6 w-80 shrink-0 text-[#e94560] hover:bg-[#16213e]/80 transition-all flex flex-col items-center justify-center gap-2 h-32"
        >
          <Plus size={32} />
          <span className="font-bold">Add Column</span>
        </button>
      </div>

      {modal.type && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4" onClick={closeModal}>
          <div className="bg-[#16213e] w-full max-w-md rounded-2xl p-8 shadow-2xl ring-1 ring-[#0f3460]" onClick={e => e.stopPropagation()}>
            <h2 className="text-2xl font-bold text-[#e94560] mb-6">
              {modal.type.includes("Note") ? (modal.type.startsWith("add") ? "New Note" : "Edit Note") : (modal.type.startsWith("add") ? "New Column" : "Edit Column")}
            </h2>
            
            <input 
              className="w-full bg-[#1a1a2e] border border-[#0f3460] rounded-lg p-3 text-white mb-4 focus:outline-none focus:ring-2 focus:ring-[#e94560]/50"
              placeholder="Title"
              value={formTitle}
              onChange={e => setFormTitle(e.target.value)}
              autoFocus
            />

            {modal.type.includes("Note") && (
              <>
                <textarea 
                  className="w-full bg-[#1a1a2e] border border-[#0f3460] rounded-lg p-3 text-white mb-4 h-32 resize-none focus:outline-none focus:ring-2 focus:ring-[#e94560]/50"
                  placeholder="Content"
                  value={formContent}
                  onChange={e => setFormContent(e.target.value)}
                />
                <div className="mb-6">
                  <label className="text-gray-500 text-sm mb-2 block">Card Color</label>
                  <div className="flex flex-wrap gap-2">
                    {NOTE_COLORS.map(c => (
                      <button 
                        key={c} 
                        onClick={() => setFormColor(c)}
                        className={`w-8 h-8 rounded-full border-2 transition-transform hover:scale-110 ${formColor === c ? 'border-[#e94560] scale-110' : 'border-transparent'}`}
                        style={{ backgroundColor: c }}
                      />
                    ))}
                  </div>
                </div>
              </>
            )}

            <div className="flex gap-3 justify-end">
              <button onClick={closeModal} className="px-6 py-2 rounded-lg bg-[#0f3460] text-gray-300 hover:bg-[#1a4a8a] transition-colors font-medium">Cancel</button>
              <button 
                onClick={modal.type.includes("Note") ? handleNoteSubmit : handleColumnSubmit}
                className="px-6 py-2 rounded-lg bg-[#e94560] text-white hover:bg-[#c73e54] transition-colors font-bold shadow-lg shadow-[#e94560]/20"
              >
                Save
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

import React, {useState, useEffect} from 'react'
import './App.css'
import { useToast } from './components/Toast'

const API_BASE = process.env.REACT_APP_API_BASE || 'http://localhost:8000'

function App(){
  const { showToast } = useToast()
  const [token, setToken] = useState(null)
  const [patientId, setPatientId] = useState('patient-123')
  const [files, setFiles] = useState([])
  const [file, setFile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')
  const [messageType, setMessageType] = useState('')

  // Helper function to handle errors and show toast
  function handleError(error, defaultMessage = 'An unexpected error occurred') {
    let errorMessage = defaultMessage
    
    if (error instanceof TypeError && error.message.includes('fetch')) {
      errorMessage = 'Network error: Unable to connect to the server. Please check your connection.'
    } else if (error.message) {
      errorMessage = error.message
    }
    
    showToast(errorMessage, 'error')
    console.error('Error:', error)
    return errorMessage
  }

  useEffect(()=>{
    async function login(){
      try {
        const res = await fetch(`${API_BASE}/auth/login`, {
          method: 'POST', 
          headers:{'Content-Type':'application/json'}, 
          body: JSON.stringify({username: 'alice'})
        })
        if (!res.ok) {
          throw new Error('Authentication failed')
        }
        const data = await res.json()
        setToken(data.access_token)
      } catch (error) {
        handleError(error, 'Failed to authenticate. Please refresh the page.')
      }
    }
    login()
  }, [showToast])

  useEffect(()=>{ if(token) loadFiles() }, [token, patientId])

  async function loadFiles(){
    try {
      setLoading(true)
      const res = await fetch(`${API_BASE}/files?patient_id=${encodeURIComponent(patientId)}`, {
        headers: {Authorization: `Bearer ${token}`}
      })
      if (!res.ok) {
        throw new Error(`Failed to load files: ${res.statusText}`)
      }
      const data = await res.json()
      setFiles(data)
    } catch (error) {
      handleError(error, 'Failed to load files. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  async function handleUpload(e){
    e.preventDefault()
    if(!file) {
      setMessage('Please select a PDF file')
      setMessageType('error')
      setTimeout(() => setMessage(''), 3000)
      return
    }
    try {
      const form = new FormData()
      form.append('patient_id', patientId)
      form.append('file', file)
      setLoading(true)
      setMessage('')
      const res = await fetch(`${API_BASE}/files/upload`, {
        method: 'POST', 
        headers: {Authorization: `Bearer ${token}`}, 
        body: form
      })
      if(!res.ok){
        let errorMessage = 'Upload failed'
        try {
          const err = await res.json()
          errorMessage = err.detail || errorMessage
        } catch {
          errorMessage = `Upload failed: ${res.statusText}`
        }
        setMessage(errorMessage)
        setMessageType('error')
        showToast(errorMessage, 'error')
        setLoading(false)
        setTimeout(() => setMessage(''), 5000)
        return
      }
      setMessage('File uploaded successfully')
      setMessageType('success')
      setFile(null)
      const fileInput = document.querySelector('input[type="file"]')
      if (fileInput) fileInput.value = ''
      await loadFiles()
      setTimeout(() => setMessage(''), 3000)
    } catch (error) {
      const errorMessage = handleError(error, 'An unexpected error occurred during upload')
      setMessage(errorMessage)
      setMessageType('error')
    } finally {
      setLoading(false)
    }
  }

  async function handleDownload(id, filename){
    try {
      setLoading(true)
      const res = await fetch(`${API_BASE}/files/${id}/download`, {
        headers: {Authorization: `Bearer ${token}`}
      })
      if(!res.ok){ 
        const errorMessage = `Download failed: ${res.statusText}`
        setMessage(errorMessage)
        setMessageType('error')
        showToast(errorMessage, 'error')
        return 
      }
      const blob = await res.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = filename
      document.body.appendChild(a)
      a.click()
      a.remove()
      window.URL.revokeObjectURL(url)
    } catch (error) {
      const errorMessage = handleError(error, 'An unexpected error occurred during download')
      setMessage(errorMessage)
      setMessageType('error')
    } finally {
      setLoading(false)
      setTimeout(() => setMessage(''), 3000)
    }
  }

  async function handleDelete(id){
    if(!window.confirm('Are you sure you want to delete this file?')) return
    try {
      setLoading(true)
      const res = await fetch(`${API_BASE}/files/${id}`, {
        method: 'DELETE', 
        headers: {Authorization: `Bearer ${token}`}
      })
      if(!res.ok){ 
        const errorMessage = `Delete failed: ${res.statusText}`
        setMessage(errorMessage)
        setMessageType('error')
        showToast(errorMessage, 'error')
        return 
      }
      setMessage('File deleted successfully')
      setMessageType('success')
      await loadFiles()
      setTimeout(() => setMessage(''), 3000)
    } catch (error) {
      const errorMessage = handleError(error, 'An unexpected error occurred during deletion')
      setMessage(errorMessage)
      setMessageType('error')
    } finally {
      setLoading(false)
    }
  }

  function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
  }

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <h1 className="app-title">
            <span className="icon">🏥</span>
            Healthcare Document Manager
          </h1>
          <p className="app-subtitle">Secure Patient Document Management System</p>
        </div>
      </header>

      <main className="app-main">
        <div className="main-layout">
          {/* Left Side - Documents List */}
          <div className="documents-panel">
            <div className="card documents-card">
              <div className="card-header">
                <h2 className="card-title">Patient Documents</h2>
                {loading && <span className="loading-indicator">Loading...</span>}
              </div>
              
              {files.length === 0 && !loading ? (
                <div className="empty-state">
                  <span className="empty-icon">📋</span>
                  <p>No documents found for this patient</p>
                </div>
              ) : (
                <div className="files-list">
                  {files.map(f=> (
                    <div key={f.id} className="file-card">
                      <div className="file-icon">📄</div>
                      <div className="file-info">
                        <h3 className="file-name">{f.filename}</h3>
                        <div className="file-meta">
                          <span className="file-size">{formatFileSize(f.size)}</span>
                          <span className="file-separator">•</span>
                          <span className="file-date">{new Date(f.uploaded_at).toLocaleString()}</span>
                        </div>
                      </div>
                      <div className="file-actions">
                        <button 
                          onClick={()=>handleDownload(f.id, f.filename)} 
                          className="btn btn-icon"
                          title="Download"
                          disabled={loading}
                        >
                          ⬇️
                        </button>
                        <button 
                          onClick={()=>handleDelete(f.id)} 
                          className="btn btn-icon btn-danger"
                          title="Delete"
                          disabled={loading}
                        >
                          🗑️
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Right Side - Patient Info and Upload */}
          <div className="upload-panel">
            <div className="card">
              <h2 className="card-title">Patient Information</h2>
              <div className="form-group">
                <label htmlFor="patient-id" className="form-label">Patient ID</label>
                <input 
                  id="patient-id"
                  type="text" 
                  className="form-input" 
                  value={patientId} 
                  onChange={e=>setPatientId(e.target.value)}
                  placeholder="Enter patient ID"
                />
              </div>
            </div>

            <div className="card">
              <h2 className="card-title">Upload Document</h2>
              <form onSubmit={handleUpload} className="upload-form">
                <div className="form-group">
                  <label htmlFor="file-upload" className="file-upload-label">
                    <span className="file-upload-icon">📄</span>
                    <span className="file-upload-text">
                      {file ? file.name : 'Choose PDF file'}
                    </span>
                    <input 
                      id="file-upload"
                      type="file" 
                      accept="application/pdf" 
                      onChange={e=>setFile(e.target.files[0])}
                      className="file-upload-input"
                    />
                  </label>
                </div>
                {message && (
                  <div className={`message message-${messageType}`}>
                    <span>{messageType === 'success' ? '✓' : '✗'}</span>
                    {message}
                  </div>
                )}
                <button 
                  type="submit" 
                  className="btn btn-primary"
                  disabled={loading || !file}
                >
                  {loading ? (
                    <>
                      <span className="spinner"></span>
                      Uploading...
                    </>
                  ) : (
                    <>
                      <span>📤</span>
                      Upload PDF
                    </>
                  )}
                </button>
              </form>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}

export default App
# SafeChild - Autopsy + Sleuth Kit Entegrasyon Yol Haritası

## 🎯 PROJE HEDEFI

SafeChild projesine %100 açık kaynak, mahkemede kabul edilebilir forensics capability eklemek.

---

## 📋 6 HAFTALI İMPLEMENTASYON PLANI

### PHASE 1: Kurulum & Setup (Hafta 1) 

#### Gün 1-2: Sleuth Kit & Autopsy Kurulumu
```bash
# Backend sunucusuna Sleuth Kit kurulumu
cd /app/backend
mkdir forensics
cd forensics

# The Sleuth Kit (TSK) kurulumu
git clone https://github.com/sleuthkit/sleuthkit.git
cd sleuthkit
./bootstrap
./configure
make
sudo make install

# Autopsy kurulumu (Java gerektirir)
cd /app/backend/forensics
git clone https://github.com/sleuthkit/autopsy.git
cd autopsy

# Dependencies
sudo apt-get update
sudo apt-get install -y openjdk-17-jdk ant
sudo apt-get install -y testdisk libafflib-dev libewf-dev

# Build Autopsy
ant
```

#### Gün 3: Python TSK Bindings
```bash
# pytsk3 - Python bindings for Sleuth Kit
pip install pytsk3

# Test installation
python3 -c "import pytsk3; print('TSK version:', pytsk3.TSK_VERSION_NUM)"
```

#### Gün 4-5: İlk Test ve Exploration
```python
# /app/backend/forensics/test_tsk.py
import pytsk3
import sys

def test_tsk_installation():
    """Test TSK installation and basic functionality"""
    print(f"pytsk3 version: {pytsk3.TSK_VERSION_NUM}")
    print(f"TSK version: {pytsk3.TSK_VERSION_STR}")
    print("✅ Sleuth Kit successfully installed!")

if __name__ == "__main__":
    test_tsk_installation()
```

---

### PHASE 2: Core Engine Development (Hafta 2-3)

#### SafeChild Forensics Engine Architecture

```
/app/backend/forensics/
├── __init__.py
├── engine.py              # Main forensics engine
├── parsers/
│   ├── __init__.py
│   ├── whatsapp.py       # WhatsApp parser
│   ├── telegram.py       # Telegram parser
│   ├── signal.py         # Signal parser
│   └── sms.py            # SMS/Call logs parser
├── analyzers/
│   ├── __init__.py
│   ├── timeline.py       # Timeline reconstruction
│   ├── contacts.py       # Contact network analysis
│   ├── media.py          # Media file analysis
│   └── deleted.py        # Deleted data recovery
├── reporters/
│   ├── __init__.py
│   ├── pdf_generator.py  # PDF report generation
│   └── html_generator.py # HTML report generation
└── utils/
    ├── __init__.py
    ├── hash.py           # Hash verification
    └── extractor.py      # File extraction utilities
```

#### Core Engine Implementation

```python
# /app/backend/forensics/engine.py

import pytsk3
import pyewf
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import hashlib
import json

class SafeChildForensicsEngine:
    """
    Main forensics engine using Sleuth Kit (TSK)
    100% Open Source - Apache 2.0 License
    """
    
    def __init__(self):
        self.tsk_version = pytsk3.TSK_VERSION_NUM
        self.output_base = Path("/app/forensic_outputs")
        self.output_base.mkdir(exist_ok=True)
        
    async def analyze_android_backup(
        self,
        backup_file: Path,
        case_id: str,
        client_info: Dict
    ) -> Dict:
        """
        Analyze Android backup file (.ab, .tar, or disk image)
        
        Args:
            backup_file: Path to backup file
            case_id: Unique case identifier
            client_info: Client information
            
        Returns:
            Analysis results with report paths
        """
        case_dir = self.output_base / case_id
        case_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"[SafeChild Forensics] Starting analysis for case: {case_id}")
        
        # Step 1: Hash verification for chain of custody
        print("[1/6] Computing file hash for chain of custody...")
        file_hash = self._compute_hash(backup_file)
        
        # Step 2: Open the backup file with TSK
        print("[2/6] Opening backup file with Sleuth Kit...")
        img_info = self._open_image(backup_file)
        
        if not img_info:
            return {
                "success": False,
                "error": "Failed to open backup file"
            }
        
        # Step 3: Extract WhatsApp data
        print("[3/6] Extracting WhatsApp data...")
        whatsapp_data = await self._extract_whatsapp(img_info, case_dir)
        
        # Step 4: Extract Telegram data
        print("[4/6] Extracting Telegram data...")
        telegram_data = await self._extract_telegram(img_info, case_dir)
        
        # Step 5: Extract SMS and call logs
        print("[5/6] Extracting SMS and call logs...")
        sms_data = await self._extract_sms(img_info, case_dir)
        
        # Step 6: Generate comprehensive report
        print("[6/6] Generating forensic report...")
        report = await self._generate_report({
            "case_id": case_id,
            "client": client_info,
            "file_hash": file_hash,
            "analysis_date": datetime.utcnow(),
            "whatsapp": whatsapp_data,
            "telegram": telegram_data,
            "sms": sms_data,
            "timeline": await self._create_timeline(
                whatsapp_data, telegram_data, sms_data
            )
        }, case_dir)
        
        print("✅ Forensic analysis completed!")
        
        return {
            "success": True,
            "case_id": case_id,
            "file_hash": file_hash,
            "report_pdf": str(report["pdf_path"]),
            "report_html": str(report["html_path"]),
            "statistics": {
                "whatsapp_messages": len(whatsapp_data.get("messages", [])),
                "whatsapp_deleted": len(whatsapp_data.get("deleted", [])),
                "telegram_messages": len(telegram_data.get("messages", [])),
                "sms_messages": len(sms_data.get("messages", [])),
                "call_logs": len(sms_data.get("calls", []))
            }
        }
    
    def _open_image(self, image_path: Path):
        """
        Open disk image/backup file using pytsk3
        """
        try:
            # Try to open as raw image
            img_info = pytsk3.Img_Info(str(image_path))
            return img_info
        except Exception as e:
            print(f"Error opening image: {e}")
            return None
    
    def _compute_hash(self, file_path: Path, algorithm='sha256'):
        """
        Compute cryptographic hash for chain of custody
        """
        hash_obj = hashlib.sha256()
        
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_obj.update(chunk)
        
        return hash_obj.hexdigest()
    
    async def _extract_whatsapp(
        self, 
        img_info, 
        case_dir: Path
    ) -> Dict:
        """
        Extract WhatsApp data from Android image
        """
        whatsapp_data = {
            "messages": [],
            "deleted": [],
            "contacts": [],
            "media": []
        }
        
        try:
            # Open filesystem
            fs_info = pytsk3.FS_Info(img_info)
            
            # WhatsApp database path in Android
            wa_db_path = "/data/data/com.whatsapp/databases/msgstore.db"
            
            # Find and extract the file
            file_obj = self._find_file(fs_info, wa_db_path)
            
            if file_obj:
                # Extract to local filesystem
                local_db = case_dir / "whatsapp_msgstore.db"
                self._extract_file(file_obj, local_db)
                
                # Parse WhatsApp database
                from .parsers.whatsapp import WhatsAppParser
                parser = WhatsAppParser()
                whatsapp_data = await parser.parse_database(local_db)
        
        except Exception as e:
            print(f"WhatsApp extraction error: {e}")
        
        return whatsapp_data
    
    async def _extract_telegram(
        self,
        img_info,
        case_dir: Path
    ) -> Dict:
        """
        Extract Telegram data from Android image
        """
        telegram_data = {
            "messages": [],
            "deleted": [],
            "contacts": []
        }
        
        try:
            fs_info = pytsk3.FS_Info(img_info)
            
            # Telegram database path
            tg_db_path = "/data/data/org.telegram.messenger/databases/cache4.db"
            
            file_obj = self._find_file(fs_info, tg_db_path)
            
            if file_obj:
                local_db = case_dir / "telegram_cache4.db"
                self._extract_file(file_obj, local_db)
                
                from .parsers.telegram import TelegramParser
                parser = TelegramParser()
                telegram_data = await parser.parse_database(local_db)
        
        except Exception as e:
            print(f"Telegram extraction error: {e}")
        
        return telegram_data
    
    async def _extract_sms(
        self,
        img_info,
        case_dir: Path
    ) -> Dict:
        """
        Extract SMS and call logs
        """
        sms_data = {
            "messages": [],
            "calls": []
        }
        
        try:
            fs_info = pytsk3.FS_Info(img_info)
            
            # Android SMS database
            sms_db_path = "/data/data/com.android.providers.telephony/databases/mmssms.db"
            
            file_obj = self._find_file(fs_info, sms_db_path)
            
            if file_obj:
                local_db = case_dir / "mmssms.db"
                self._extract_file(file_obj, local_db)
                
                from .parsers.sms import SMSParser
                parser = SMSParser()
                sms_data = await parser.parse_database(local_db)
        
        except Exception as e:
            print(f"SMS extraction error: {e}")
        
        return sms_data
    
    def _find_file(self, fs_info, file_path: str):
        """
        Find file in filesystem by path
        """
        try:
            return fs_info.open(file_path)
        except:
            return None
    
    def _extract_file(self, file_obj, output_path: Path):
        """
        Extract file from image to local filesystem
        """
        with open(output_path, 'wb') as f:
            offset = 0
            size = file_obj.info.meta.size
            
            while offset < size:
                available = min(1024 * 1024, size - offset)  # 1MB chunks
                data = file_obj.read_random(offset, available)
                f.write(data)
                offset += len(data)
    
    async def _create_timeline(
        self,
        whatsapp_data: Dict,
        telegram_data: Dict,
        sms_data: Dict
    ) -> List[Dict]:
        """
        Create chronological timeline of all communications
        """
        timeline = []
        
        # Add WhatsApp messages to timeline
        for msg in whatsapp_data.get("messages", []):
            timeline.append({
                "timestamp": msg.get("timestamp"),
                "type": "WhatsApp",
                "from": msg.get("from"),
                "to": msg.get("to"),
                "content": msg.get("content"),
                "deleted": False
            })
        
        # Add deleted WhatsApp messages
        for msg in whatsapp_data.get("deleted", []):
            timeline.append({
                "timestamp": msg.get("timestamp"),
                "type": "WhatsApp (Deleted)",
                "from": msg.get("from"),
                "to": msg.get("to"),
                "content": msg.get("content"),
                "deleted": True
            })
        
        # Add Telegram messages
        for msg in telegram_data.get("messages", []):
            timeline.append({
                "timestamp": msg.get("timestamp"),
                "type": "Telegram",
                "from": msg.get("from"),
                "to": msg.get("to"),
                "content": msg.get("content"),
                "deleted": False
            })
        
        # Add SMS
        for msg in sms_data.get("messages", []):
            timeline.append({
                "timestamp": msg.get("timestamp"),
                "type": "SMS",
                "from": msg.get("from"),
                "to": msg.get("to"),
                "content": msg.get("content"),
                "deleted": False
            })
        
        # Sort by timestamp
        timeline.sort(key=lambda x: x.get("timestamp", 0))
        
        return timeline
    
    async def _generate_report(
        self,
        data: Dict,
        case_dir: Path
    ) -> Dict:
        """
        Generate PDF and HTML forensic reports
        """
        from .reporters.pdf_generator import PDFReportGenerator
        from .reporters.html_generator import HTMLReportGenerator
        
        pdf_gen = PDFReportGenerator()
        html_gen = HTMLReportGenerator()
        
        pdf_path = case_dir / f"SafeChild_Forensic_Report_{data['case_id']}.pdf"
        html_path = case_dir / f"SafeChild_Forensic_Report_{data['case_id']}.html"
        
        await pdf_gen.generate(data, pdf_path)
        await html_gen.generate(data, html_path)
        
        return {
            "pdf_path": pdf_path,
            "html_path": html_path
        }
```

---

### PHASE 3: Parser Development (Hafta 3)

#### WhatsApp Parser

```python
# /app/backend/forensics/parsers/whatsapp.py

import sqlite3
from pathlib import Path
from typing import Dict, List
from datetime import datetime

class WhatsAppParser:
    """
    Parse WhatsApp msgstore.db database
    """
    
    async def parse_database(self, db_path: Path) -> Dict:
        """
        Parse WhatsApp database and extract all messages
        """
        if not db_path.exists():
            return {"messages": [], "deleted": [], "contacts": [], "media": []}
        
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Parse messages
        messages = self._parse_messages(cursor)
        
        # Parse deleted messages (from WAL/freelist)
        deleted = self._parse_deleted_messages(cursor, db_path)
        
        # Parse contacts
        contacts = self._parse_contacts(cursor)
        
        # Parse media
        media = self._parse_media(cursor)
        
        conn.close()
        
        return {
            "messages": messages,
            "deleted": deleted,
            "contacts": contacts,
            "media": media
        }
    
    def _parse_messages(self, cursor) -> List[Dict]:
        """
        Parse regular messages from WhatsApp database
        """
        query = """
            SELECT 
                _id,
                key_remote_jid as contact,
                key_from_me,
                data as content,
                timestamp,
                media_url,
                media_mime_type,
                media_size,
                latitude,
                longitude,
                received_timestamp
            FROM messages
            WHERE key_remote_jid IS NOT NULL
            ORDER BY timestamp DESC
        """
        
        try:
            cursor.execute(query)
            rows = cursor.fetchall()
            
            messages = []
            for row in rows:
                messages.append({
                    "id": row[0],
                    "contact": row[1],
                    "from_me": bool(row[2]),
                    "content": row[3],
                    "timestamp": row[4],
                    "media_url": row[5],
                    "media_type": row[6],
                    "media_size": row[7],
                    "latitude": row[8],
                    "longitude": row[9],
                    "received_timestamp": row[10]
                })
            
            return messages
        
        except sqlite3.Error as e:
            print(f"Error parsing WhatsApp messages: {e}")
            return []
    
    def _parse_deleted_messages(self, cursor, db_path: Path) -> List[Dict]:
        """
        Parse deleted messages from SQLite freelists and WAL
        """
        deleted = []
        
        # Check for WAL file
        wal_path = Path(str(db_path) + "-wal")
        
        if wal_path.exists():
            # Parse WAL for deleted records
            # This is simplified - real implementation needs deep SQLite forensics
            try:
                cursor.execute("PRAGMA freelist_count")
                freelist_count = cursor.fetchone()[0]
                
                if freelist_count > 0:
                    deleted.append({
                        "info": f"Found {freelist_count} freelist pages",
                        "recovery_possible": True,
                        "note": "Detailed deleted message recovery available"
                    })
            except:
                pass
        
        return deleted
    
    def _parse_contacts(self, cursor) -> List[Dict]:
        """
        Parse contacts from WhatsApp
        """
        query = """
            SELECT DISTINCT
                jid,
                display_name,
                number
            FROM wa_contacts
        """
        
        try:
            cursor.execute(query)
            rows = cursor.fetchall()
            
            contacts = []
            for row in rows:
                contacts.append({
                    "jid": row[0],
                    "name": row[1],
                    "number": row[2]
                })
            
            return contacts
        
        except:
            return []
    
    def _parse_media(self, cursor) -> List[Dict]:
        """
        Parse media files metadata
        """
        query = """
            SELECT 
                _id,
                media_url,
                media_mime_type,
                media_size,
                file_path
            FROM messages
            WHERE media_url IS NOT NULL
        """
        
        try:
            cursor.execute(query)
            rows = cursor.fetchall()
            
            media = []
            for row in rows:
                media.append({
                    "id": row[0],
                    "url": row[1],
                    "type": row[2],
                    "size": row[3],
                    "path": row[4]
                })
            
            return media
        
        except:
            return []
```

---

### PHASE 4: Backend API (Hafta 4)

#### FastAPI Endpoints

```python
# /app/backend/server.py (add to existing)

from forensics.engine import SafeChildForensicsEngine
from fastapi import UploadFile, File, BackgroundTasks
import shutil

# Initialize forensics engine
forensics_engine = SafeChildForensicsEngine()

# ==================== FORENSICS ENDPOINTS ====================

@api_router.post("/forensics/analyze")
async def start_forensic_analysis(
    backup_file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None,
    current_client: dict = Depends(get_current_client)
):
    """
    Upload device backup and start forensic analysis
    Supports: .ab (Android Backup), .tar, .img (disk images)
    """
    case_id = f"CASE_{current_client['clientNumber']}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
    
    # Save uploaded file
    upload_dir = Path("/tmp/forensics_uploads")
    upload_dir.mkdir(exist_ok=True)
    
    file_path = upload_dir / f"{case_id}_{backup_file.filename}"
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(backup_file.file, buffer)
    
    # Start analysis in background
    analysis_record = {
        "case_id": case_id,
        "client_number": current_client["clientNumber"],
        "client_email": current_client["email"],
        "status": "processing",
        "uploaded_file": str(file_path),
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    await db.forensic_analyses.insert_one(analysis_record)
    
    # Run analysis asynchronously
    background_tasks.add_task(
        run_forensic_analysis,
        file_path,
        case_id,
        {
            "clientNumber": current_client["clientNumber"],
            "email": current_client["email"],
            "firstName": current_client.get("firstName", ""),
            "lastName": current_client.get("lastName", "")
        }
    )
    
    return {
        "success": True,
        "case_id": case_id,
        "message": "Forensic analysis started. You will be notified when complete.",
        "estimated_time": "5-15 minutes"
    }

async def run_forensic_analysis(file_path: Path, case_id: str, client_info: Dict):
    """
    Background task to run forensic analysis
    """
    try:
        result = await forensics_engine.analyze_android_backup(
            file_path,
            case_id,
            client_info
        )
        
        # Update database
        await db.forensic_analyses.update_one(
            {"case_id": case_id},
            {"$set": {
                "status": "completed",
                "completed_at": datetime.utcnow(),
                "report_pdf": result.get("report_pdf"),
                "report_html": result.get("report_html"),
                "file_hash": result.get("file_hash"),
                "statistics": result.get("statistics"),
                "updated_at": datetime.utcnow()
            }}
        )
        
        # Send notification to client
        # TODO: Implement email notification
        
    except Exception as e:
        # Update with error
        await db.forensic_analyses.update_one(
            {"case_id": case_id},
            {"$set": {
                "status": "failed",
                "error": str(e),
                "updated_at": datetime.utcnow()
            }}
        )

@api_router.get("/forensics/status/{case_id}")
async def get_forensic_status(
    case_id: str,
    current_client: dict = Depends(get_current_client)
):
    """
    Get forensic analysis status
    """
    analysis = await db.forensic_analyses.find_one({
        "case_id": case_id,
        "client_number": current_client["clientNumber"]
    })
    
    if not analysis:
        raise HTTPException(status_code=404, detail="Case not found")
    
    return {
        "case_id": case_id,
        "status": analysis["status"],
        "created_at": analysis["created_at"],
        "updated_at": analysis["updated_at"],
        "completed_at": analysis.get("completed_at"),
        "statistics": analysis.get("statistics"),
        "error": analysis.get("error")
    }

@api_router.get("/forensics/report/{case_id}")
async def download_forensic_report(
    case_id: str,
    format: str = "pdf",  # pdf or html
    current_client: dict = Depends(get_current_client)
):
    """
    Download forensic report
    """
    analysis = await db.forensic_analyses.find_one({
        "case_id": case_id,
        "client_number": current_client["clientNumber"]
    })
    
    if not analysis:
        raise HTTPException(status_code=404, detail="Case not found")
    
    if analysis["status"] != "completed":
        raise HTTPException(status_code=400, detail="Analysis not completed yet")
    
    report_path = analysis.get(f"report_{format}")
    
    if not report_path or not Path(report_path).exists():
        raise HTTPException(status_code=404, detail=f"Report ({format}) not found")
    
    return FileResponse(
        report_path,
        media_type="application/pdf" if format == "pdf" else "text/html",
        filename=f"SafeChild_Report_{case_id}.{format}"
    )

@api_router.get("/forensics/my-cases")
async def get_my_forensic_cases(
    current_client: dict = Depends(get_current_client)
):
    """
    Get all forensic cases for current client
    """
    cases = await db.forensic_analyses.find(
        {"client_number": current_client["clientNumber"]},
        {"_id": 0}
    ).sort("created_at", -1).to_list(None)
    
    return cases
```

---

### PHASE 5: Frontend UI (Hafta 5)

#### React Forensics Page

```jsx
// /app/frontend/src/pages/ForensicAnalysis.jsx

import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useLanguage } from '../contexts/LanguageContext';
import { Card, CardHeader, CardContent, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Alert, AlertDescription } from '../components/ui/alert';
import { Upload, FileCheck, Download, Clock, CheckCircle, XCircle } from 'lucide-react';
import axios from 'axios';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const ForensicAnalysis = () => {
  const { user, token } = useAuth();
  const { language } = useLanguage();
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [cases, setCases] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (user && token) {
      loadMyCases();
    }
  }, [user, token]);

  const loadMyCases = async () => {
    try {
      const response = await axios.get(
        `${BACKEND_URL}/api/forensics/my-cases`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setCases(response.data);
    } catch (error) {
      toast.error('Error loading cases');
    } finally {
      setLoading(false);
    }
  };

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    setFile(selectedFile);
  };

  const handleUpload = async () => {
    if (!file) {
      toast.error(
        language === 'de' ? 'Bitte wählen Sie eine Datei' : 'Please select a file'
      );
      return;
    }

    setUploading(true);

    const formData = new FormData();
    formData.append('backup_file', file);

    try {
      const response = await axios.post(
        `${BACKEND_URL}/api/forensics/analyze`,
        formData,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'multipart/form-data'
          }
        }
      );

      toast.success(
        language === 'de' 
          ? 'Analyse gestartet! Sie werden benachrichtigt, wenn sie abgeschlossen ist.' 
          : 'Analysis started! You will be notified when complete.'
      );

      setFile(null);
      loadMyCases();
    } catch (error) {
      toast.error(
        language === 'de' 
          ? 'Fehler beim Hochladen' 
          : 'Upload error',
        { description: error.response?.data?.detail || error.message }
      );
    } finally {
      setUploading(false);
    }
  };

  const handleDownload = async (caseId, format = 'pdf') => {
    try {
      const response = await axios.get(
        `${BACKEND_URL}/api/forensics/report/${caseId}?format=${format}`,
        {
          headers: { Authorization: `Bearer ${token}` },
          responseType: 'blob'
        }
      );

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `SafeChild_Report_${caseId}.${format}`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      toast.error('Error downloading report');
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-600" />;
      case 'processing':
        return <Clock className="w-5 h-5 text-blue-600 animate-spin" />;
      case 'failed':
        return <XCircle className="w-5 h-5 text-red-600" />;
      default:
        return null;
    }
  };

  const getStatusText = (status) => {
    const texts = {
      'processing': language === 'de' ? 'Verarbeitung...' : 'Processing...',
      'completed': language === 'de' ? 'Abgeschlossen' : 'Completed',
      'failed': language === 'de' ? 'Fehlgeschlagen' : 'Failed'
    };
    return texts[status] || status;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50 py-12">
      <div className="container mx-auto px-4">
        <h1 className="text-4xl font-bold text-center mb-8">
          {language === 'de' ? 'Forensische Analyse' : 'Forensic Analysis'}
        </h1>

        {/* Upload Section */}
        <Card className="mb-8 max-w-3xl mx-auto">
          <CardHeader>
            <CardTitle>
              {language === 'de' ? 'Neue Analyse starten' : 'Start New Analysis'}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <Alert className="mb-6 border-blue-200 bg-blue-50">
              <AlertDescription className="text-blue-900">
                <strong>{language === 'de' ? 'Unterstützte Formate:' : 'Supported formats:'}</strong>
                <br />
                • Android Backup (.ab, .tar)
                <br />
                • Disk Images (.img, .dd)
                <br />
                • WhatsApp Database (.db)
              </AlertDescription>
            </Alert>

            <div className="space-y-4">
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
                <Upload className="w-12 h-12 mx-auto mb-4 text-gray-400" />
                <input
                  type="file"
                  onChange={handleFileChange}
                  accept=".ab,.tar,.img,.dd,.db,.zip"
                  className="mb-4"
                />
                {file && (
                  <p className="text-sm text-green-600 mt-2">
                    ✓ {file.name} ({(file.size / 1024 / 1024).toFixed(2)} MB)
                  </p>
                )}
              </div>

              <Button
                onClick={handleUpload}
                disabled={!file || uploading}
                className="w-full bg-blue-600 hover:bg-blue-700"
                size="lg"
              >
                {uploading ? (
                  <>
                    <Clock className="w-5 h-5 mr-2 animate-spin" />
                    {language === 'de' ? 'Hochladen...' : 'Uploading...'}
                  </>
                ) : (
                  <>
                    <FileCheck className="w-5 h-5 mr-2" />
                    {language === 'de' ? 'Analyse starten' : 'Start Analysis'}
                  </>
                )}
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Cases List */}
        <div className="max-w-5xl mx-auto">
          <h2 className="text-2xl font-bold mb-4">
            {language === 'de' ? 'Meine Fälle' : 'My Cases'}
          </h2>

          {loading ? (
            <div className="text-center py-8">
              <Clock className="w-8 h-8 mx-auto mb-2 animate-spin text-blue-600" />
              <p>{language === 'de' ? 'Lädt...' : 'Loading...'}</p>
            </div>
          ) : cases.length === 0 ? (
            <Card>
              <CardContent className="p-8 text-center text-gray-500">
                {language === 'de' 
                  ? 'Keine Fälle gefunden. Starten Sie Ihre erste Analyse oben.' 
                  : 'No cases found. Start your first analysis above.'}
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-4">
              {cases.map((caseItem) => (
                <Card key={caseItem.case_id} className="border-2">
                  <CardContent className="p-6">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-2">
                          {getStatusIcon(caseItem.status)}
                          <h3 className="font-bold text-lg">{caseItem.case_id}</h3>
                        </div>
                        <p className="text-sm text-gray-600 mb-2">
                          {language === 'de' ? 'Status:' : 'Status:'} {getStatusText(caseItem.status)}
                        </p>
                        <p className="text-xs text-gray-500">
                          {language === 'de' ? 'Erstellt:' : 'Created:'} {new Date(caseItem.created_at).toLocaleString()}
                        </p>
                        
                        {caseItem.statistics && (
                          <div className="mt-3 grid grid-cols-2 gap-2 text-sm">
                            <div className="bg-green-50 p-2 rounded">
                              <strong>WhatsApp:</strong> {caseItem.statistics.whatsapp_messages} messages
                            </div>
                            {caseItem.statistics.whatsapp_deleted > 0 && (
                              <div className="bg-yellow-50 p-2 rounded">
                                <strong>Deleted:</strong> {caseItem.statistics.whatsapp_deleted} recovered
                              </div>
                            )}
                            {caseItem.statistics.telegram_messages > 0 && (
                              <div className="bg-blue-50 p-2 rounded">
                                <strong>Telegram:</strong> {caseItem.statistics.telegram_messages} messages
                              </div>
                            )}
                            {caseItem.statistics.sms_messages > 0 && (
                              <div className="bg-purple-50 p-2 rounded">
                                <strong>SMS:</strong> {caseItem.statistics.sms_messages} messages
                              </div>
                            )}
                          </div>
                        )}
                      </div>

                      {caseItem.status === 'completed' && (
                        <div className="flex flex-col space-y-2 ml-4">
                          <Button
                            onClick={() => handleDownload(caseItem.case_id, 'pdf')}
                            size="sm"
                            className="bg-red-600 hover:bg-red-700"
                          >
                            <Download className="w-4 h-4 mr-1" />
                            PDF
                          </Button>
                          <Button
                            onClick={() => handleDownload(caseItem.case_id, 'html')}
                            size="sm"
                            variant="outline"
                          >
                            <Download className="w-4 h-4 mr-1" />
                            HTML
                          </Button>
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ForensicAnalysis;
```

---

### PHASE 6: Testing & Launch (Hafta 6)

#### Test Protocol

```bash
# Test 1: TSK Installation
python3 /app/backend/forensics/test_tsk.py

# Test 2: Sample Android Backup Analysis
# (Provide test .ab file)

# Test 3: WhatsApp Database Parsing
# Test 4: Report Generation
# Test 5: End-to-end API test
# Test 6: Frontend integration test
```

---

## 📦 DEPENDENCİES

### Backend Requirements

```txt
# /app/backend/requirements.txt (ekle)

# Forensics
pytsk3==20240714.2
pyewf==20230501
reportlab==4.0.7
Pillow==10.1.0
```

### System Requirements

```bash
# Ubuntu/Debian
sudo apt-get install -y \
    build-essential \
    autoconf \
    libtool \
    pkg-config \
    libafflib-dev \
    libewf-dev \
    libvhdi-dev \
    libvmdk-dev \
    openjdk-17-jdk \
    ant
```

---

## 🚀 İLK ADIMLAR (Şimdi Yapacağız)

### Adım 1: Dependencies Kurulumu

```bash
cd /app/backend

# System dependencies
sudo apt-get update
sudo apt-get install -y build-essential autoconf libtool pkg-config

# Install pytsk3
pip install pytsk3

# Test
python3 -c "import pytsk3; print('✅ pytsk3 installed!')"
```

### Adım 2: Forensics Klasör Yapısı

```bash
cd /app/backend
mkdir -p forensics/{parsers,analyzers,reporters,utils}
touch forensics/__init__.py
touch forensics/engine.py
touch forensics/parsers/{__init__.py,whatsapp.py,telegram.py,sms.py}
```

---

## ✅ SUCCESS KRİTERLERİ

- [ ] pytsk3 successfully installed
- [ ] Can open and read disk images
- [ ] WhatsApp database extraction working
- [ ] Telegram database extraction working
- [ ] Timeline generation working
- [ ] PDF report generation working
- [ ] Backend API endpoints working
- [ ] Frontend upload/download working
- [ ] End-to-end test successful

---

**SONRAKİ ADIM: Hemen başlayalım! Şimdi dependencies kuralım mı?** 🚀

"use client";

import { useState, useEffect } from 'react';
import { useSearchParams } from 'next/navigation';
import { api } from '@/lib/api';
import { 
  ShieldAlert, Activity, Users, Building, GraduationCap, 
  HelpCircle, Clock, CheckCircle2, AlertTriangle, Key 
} from 'lucide-react';

export default function AdminDashboard() {
  const searchParams = useSearchParams();
  const tab = searchParams.get('tab') || 'overview';
  
  const [stats, setStats] = useState<any>(null);
  const [auditLogs, setAuditLogs] = useState<any[]>([]);
  const [depts, setDepts] = useState<any[]>([]);
  const [faculty, setFaculty] = useState<any[]>([]);
  const [students, setStudents] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAdminData = async () => {
      try {
        setLoading(true);
        // Dashboard Stats
        const statsRes = await api.get('/analytics/dashboard-stats');
        setStats(statsRes.data);
        
        // Departments
        const deptsRes = await api.get('/users/departments');
        setDepts(deptsRes.data);

        // Faculty
        if (tab === 'faculty') {
          const facRes = await api.get('/users/faculty');
          setFaculty(facRes.data);
        }
        
        // Students
        if (tab === 'students') {
          const stdRes = await api.get('/users/students');
          setStudents(stdRes.data);
        }

        // Audit Logs
        if (tab === 'audit') {
          const logsRes = await api.get('/reports/audit-logs');
          setAuditLogs(logsRes.data);
        }
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    };
    fetchAdminData();
  }, [tab]);

  if (loading || !stats) {
    return (
      <div className="flex items-center justify-center py-24">
        <div className="w-10 h-10 border-2 border-[#D4AF37]/20 border-t-[#D4AF37] rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Dashboard Brand Header */}
      <div className="flex items-center justify-between border-b border-[#D4AF37]/10 pb-4">
        <div>
          <h1 className="text-3xl font-bold text-white leading-tight">Administration Center</h1>
          <p className="text-xs text-gray-500 mt-1">Manage institutional configurations, auditor trails, and system statistics.</p>
        </div>
      </div>

      {tab === 'overview' && (
        <div className="space-y-8">
          {/* Quick Metrics Bar */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="glass-card p-5 rounded-xl flex items-center space-x-4">
              <div className="bg-[#D4AF37]/10 p-3 rounded-lg border border-[#D4AF37]/20 text-[#D4AF37]">
                <GraduationCap className="w-6 h-6" />
              </div>
              <div>
                <h4 className="text-gray-400 text-xs uppercase tracking-wider font-semibold">Total Students</h4>
                <p className="text-2xl font-bold text-white mt-1">{stats.total_students}</p>
              </div>
            </div>
            
            <div className="glass-card p-5 rounded-xl flex items-center space-x-4">
              <div className="bg-green-500/10 p-3 rounded-lg border border-green-500/20 text-green-400">
                <CheckCircle2 className="w-6 h-6" />
              </div>
              <div>
                <h4 className="text-gray-400 text-xs uppercase tracking-wider font-semibold">Graded Scripts</h4>
                <p className="text-2xl font-bold text-white mt-1">{stats.processed}</p>
              </div>
            </div>

            <div className="glass-card p-5 rounded-xl flex items-center space-x-4">
              <div className="bg-[#D4AF37]/10 p-3 rounded-lg border border-[#D4AF37]/20 text-[#D4AF37]">
                <Clock className="w-6 h-6" />
              </div>
              <div>
                <h4 className="text-gray-400 text-xs uppercase tracking-wider font-semibold">Active Queue</h4>
                <p className="text-2xl font-bold text-white mt-1">{stats.remaining}</p>
              </div>
            </div>

            <div className="glass-card p-5 rounded-xl flex items-center space-x-4">
              <div className="bg-red-500/10 p-3 rounded-lg border border-red-500/20 text-red-400">
                <AlertTriangle className="w-6 h-6" />
              </div>
              <div>
                <h4 className="text-gray-400 text-xs uppercase tracking-wider font-semibold">Low Confidence</h4>
                <p className="text-2xl font-bold text-white mt-1">{stats.low_confidence_count}</p>
              </div>
            </div>
          </div>

          {/* Accuracies section */}
          <div className="grid md:grid-cols-2 gap-6">
            <div className="glass-card p-6 rounded-2xl space-y-4">
              <h3 className="text-md font-semibold text-white">OCR Layout Parsing Performance</h3>
              <div className="flex items-end space-x-2">
                <span className="text-4xl font-bold text-gold">{stats.ocr_accuracy}%</span>
                <span className="text-xs text-gray-500 pb-1">Average extraction precision</span>
              </div>
              <p className="text-xs text-gray-500 leading-relaxed">
                Aggregated accuracy is calculated based on characters match compared directly to text segmentation templates.
              </p>
            </div>

            <div className="glass-card p-6 rounded-2xl space-y-4">
              <h3 className="text-md font-semibold text-white">AI Evaluator Precision</h3>
              <div className="flex items-end space-x-2">
                <span className="text-4xl font-bold text-gold">{stats.ai_accuracy}%</span>
                <span className="text-xs text-gray-500 pb-1">LLM alignment index</span>
              </div>
              <p className="text-xs text-gray-500 leading-relaxed">
                Calculated by measuring discrepancies between the initial auto-evaluations and subsequent human override corrections.
              </p>
            </div>
          </div>
        </div>
      )}

      {tab === 'departments' && (
        <div className="glass-card p-6 rounded-2xl">
          <h3 className="text-lg font-semibold text-white mb-4">Academic Departments ({depts.length})</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {depts.map((d) => (
              <div key={d.id} className="bg-[#121214]/60 border border-gray-800 p-4 rounded-xl flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="bg-[#D4AF37]/15 p-2.5 rounded-lg text-gold border border-[#D4AF37]/25">
                    <Building className="w-5 h-5" />
                  </div>
                  <div>
                    <h4 className="text-white text-sm font-semibold">{d.name}</h4>
                    <p className="text-[10px] text-gray-500">Code identifier: {d.code}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {tab === 'faculty' && (
        <div className="glass-card p-6 rounded-2xl">
          <h3 className="text-lg font-semibold text-white mb-4">Faculty Members Register</h3>
          <div className="overflow-x-auto">
            <table className="custom-table text-sm">
              <thead>
                <tr className="text-gray-500 text-xs uppercase tracking-wider">
                  <th className="text-left font-semibold">Faculty Name</th>
                  <th className="text-left font-semibold">Email</th>
                  <th className="text-center font-semibold">Department</th>
                  <th className="text-center font-semibold">Designation</th>
                </tr>
              </thead>
              <tbody>
                {faculty.map((f) => (
                  <tr key={f.id} className="border-b border-[#D4AF37]/5 text-gray-300">
                    <td className="font-semibold text-white">{f.name}</td>
                    <td>{f.email}</td>
                    <td className="text-center">{f.department}</td>
                    <td className="text-center">
                      <span className="bg-[#121214] border border-[#D4AF37]/25 text-gold text-[10px] px-2 py-0.5 rounded font-medium">
                        {f.designation}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {tab === 'students' && (
        <div className="glass-card p-6 rounded-2xl">
          <h3 className="text-lg font-semibold text-white mb-4">Student Enrollment List</h3>
          <div className="overflow-x-auto">
            <table className="custom-table text-sm">
              <thead>
                <tr className="text-gray-500 text-xs uppercase tracking-wider">
                  <th className="text-left font-semibold">Student Name</th>
                  <th className="text-left font-semibold">Register Number</th>
                  <th className="text-left font-semibold">Email</th>
                  <th className="text-center font-semibold">Course</th>
                  <th className="text-center font-semibold">Semester</th>
                </tr>
              </thead>
              <tbody>
                {students.map((s) => (
                  <tr key={s.id} className="border-b border-[#D4AF37]/5 text-gray-300">
                    <td className="font-semibold text-white">{s.name}</td>
                    <td className="font-mono text-gold text-xs">{s.register_number}</td>
                    <td>{s.email}</td>
                    <td className="text-center">{s.course}</td>
                    <td className="text-center">Sem-{s.semester}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {tab === 'audit' && (
        <div className="glass-card p-6 rounded-2xl">
          <h3 className="text-lg font-semibold text-white mb-4 flex items-center space-x-2">
            <Activity className="text-gold w-5 h-5" />
            <span>Institutional Activity & System Logs</span>
          </h3>
          <div className="space-y-3 font-mono text-xs">
            {auditLogs.length === 0 ? (
              <div className="text-gray-500 text-center py-6">No audit lines found. Perform operations to populate records.</div>
            ) : (
              auditLogs.map((log) => (
                <div key={log.id} className="bg-[#121214]/60 border border-gray-800/80 p-3 rounded-lg flex items-start justify-between">
                  <div className="space-y-1">
                    <div className="flex items-center space-x-2">
                      <span className="bg-gold/15 border border-gold/30 text-gold text-[9px] px-1.5 py-0.5 rounded font-bold uppercase">
                        {log.action}
                      </span>
                      <span className="text-gray-400">{log.details}</span>
                    </div>
                    <div className="text-[10px] text-gray-500">
                      User: {log.user_email} | IP: {log.ip_address || "127.0.0.1"}
                    </div>
                  </div>
                  <div className="text-[10px] text-gray-500">
                    {new Date(log.timestamp).toLocaleTimeString()}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
}

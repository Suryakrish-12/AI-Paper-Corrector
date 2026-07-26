"use client";

import { useState, useEffect } from 'react';
import { useSearchParams } from 'next/navigation';
import { api } from '@/lib/api';
import { 
  Building, BookOpen, Users, LineChart, Award, FileText, 
  HelpCircle, ChevronRight, CheckCircle2, TrendingUp 
} from 'lucide-react';
import { 
  ResponsiveContainer, BarChart, Bar, XAxis, YAxis, 
  Tooltip, CartesianGrid, Legend, LineChart as RechartsLineChart, Line 
} from 'recharts';

export default function HodDashboard() {
  const searchParams = useSearchParams();
  const tab = searchParams.get('tab') || 'overview';
  
  const [deptData, setDeptData] = useState<any>(null);
  const [subData, setSubData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchHodData = async () => {
      try {
        setLoading(true);
        const instRes = await api.get('/analytics/institution-analytics');
        setDeptData(instRes.data);
        const subRes = await api.get('/analytics/subject-analytics');
        setSubData(subRes.data);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    };
    fetchHodData();
  }, []);

  if (loading || !deptData) {
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
          <h1 className="text-3xl font-bold text-white leading-tight">Academic Oversight</h1>
          <p className="text-xs text-gray-500 mt-1">Review department analytics, subject masteries, and grading trends.</p>
        </div>
      </div>

      {tab === 'overview' && (
        <div className="space-y-8">
          {/* Quick Metrics Bar */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="glass-card p-5 rounded-xl flex items-center space-x-4">
              <div className="bg-[#D4AF37]/10 p-3 rounded-lg border border-[#D4AF37]/20 text-[#D4AF37]">
                <Building className="w-6 h-6" />
              </div>
              <div>
                <h4 className="text-gray-400 text-xs uppercase tracking-wider font-semibold">Department Average</h4>
                <p className="text-2xl font-bold text-white mt-1">79.2%</p>
              </div>
            </div>
            
            <div className="glass-card p-5 rounded-xl flex items-center space-x-4">
              <div className="bg-[#D4AF37]/10 p-3 rounded-lg border border-[#D4AF37]/20 text-[#D4AF37]">
                <CheckCircle2 className="w-6 h-6" />
              </div>
              <div>
                <h4 className="text-gray-400 text-xs uppercase tracking-wider font-semibold">Pass Percentage</h4>
                <p className="text-2xl font-bold text-white mt-1">94.0%</p>
              </div>
            </div>

            <div className="glass-card p-5 rounded-xl flex items-center space-x-4">
              <div className="bg-[#D4AF37]/10 p-3 rounded-lg border border-[#D4AF37]/20 text-[#D4AF37]">
                <Users className="w-6 h-6" />
              </div>
              <div>
                <h4 className="text-gray-400 text-xs uppercase tracking-wider font-semibold">Total Students</h4>
                <p className="text-2xl font-bold text-white mt-1">142</p>
              </div>
            </div>

            <div className="glass-card p-5 rounded-xl flex items-center space-x-4">
              <div className="bg-[#D4AF37]/10 p-3 rounded-lg border border-[#D4AF37]/20 text-[#D4AF37]">
                <BookOpen className="w-6 h-6" />
              </div>
              <div>
                <h4 className="text-gray-400 text-xs uppercase tracking-wider font-semibold">Active Subjects</h4>
                <p className="text-2xl font-bold text-white mt-1">8</p>
              </div>
            </div>
          </div>

          {/* Department Comparison Chart */}
          <div className="glass-card p-6 rounded-2xl">
            <h3 className="text-md font-semibold text-white mb-4">Department Comparison (Averages & Pass Rates)</h3>
            <div className="h-72 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={deptData.departments_comparison}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#222" />
                  <XAxis dataKey="department" stroke="#666" fontSize={10} />
                  <YAxis stroke="#666" fontSize={10} />
                  <Tooltip contentStyle={{ backgroundColor: '#18181B', border: '1px solid #D4AF37' }} />
                  <Legend />
                  <Bar dataKey="avg_marks" name="Average Marks %" fill="#D4AF37" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="pass_pct" name="Pass Rate %" fill="#AA7C11" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      )}

      {tab === 'faculty' && (
        <div className="glass-card p-6 rounded-2xl">
          <h3 className="text-lg font-semibold text-white mb-4">CSE Department Faculty Comparison</h3>
          <div className="space-y-4">
            {[
              { name: 'Dr. Ramesh Chandra', subject: 'Algorithms (CS-302)', avg: 79.2, scripts: 45, confidence: 92 },
              { name: 'Prof. Amit Sharma', subject: 'Data Structures (CS-101)', avg: 82.5, scripts: 42, confidence: 94 },
              { name: 'Dr. Sunita Sen', subject: 'Computer Networks (CS-304)', avg: 71.0, scripts: 48, confidence: 89 }
            ].map((fac, idx) => (
              <div key={idx} className="flex items-center justify-between bg-[#121214]/50 border border-gray-800 p-4 rounded-xl">
                <div>
                  <h4 className="text-white text-sm font-semibold">{fac.name}</h4>
                  <p className="text-[10px] text-gray-500">{fac.subject}</p>
                </div>
                <div className="flex space-x-8 text-xs text-right">
                  <div>
                    <span className="block text-[10px] text-gray-500">Evaluated Bundle</span>
                    <span className="font-semibold text-white">{fac.scripts} Scripts</span>
                  </div>
                  <div>
                    <span className="block text-[10px] text-gray-500">Class Avg</span>
                    <span className="font-semibold text-gold">{fac.avg}%</span>
                  </div>
                  <div>
                    <span className="block text-[10px] text-gray-500">AI Confidence</span>
                    <span className="font-semibold text-green-400">{fac.confidence}%</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {tab === 'subjects' && subData && (
        <div className="grid md:grid-cols-12 gap-6">
          <div className="md:col-span-8 glass-card p-6 rounded-2xl">
            <h3 className="text-md font-semibold text-white mb-4">Subject Concept Mastery Detail ({subData.subject_name})</h3>
            <div className="h-64 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={subData.concept_mastery}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#222" />
                  <XAxis dataKey="concept" stroke="#666" fontSize={9} />
                  <YAxis stroke="#666" domain={[0, 100]} fontSize={10} />
                  <Tooltip contentStyle={{ backgroundColor: '#18181B', border: '1px solid #D4AF37' }} />
                  <Bar dataKey="mastery" fill="#D4AF37" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="md:col-span-4 glass-card p-6 rounded-2xl flex flex-col justify-between">
            <div>
              <h3 className="text-sm font-bold text-white uppercase tracking-wider mb-4 flex items-center space-x-1.5">
                <TrendingUp className="w-4 h-4 text-gold" />
                <span>Critical Weak Point</span>
              </h3>
              <div className="bg-red-500/5 border border-red-500/15 p-4 rounded-xl space-y-3">
                <div className="flex justify-between text-xs">
                  <span className="font-bold text-red-400">{subData.most_incorrect_question.question_number}</span>
                  <span className="text-gray-400">Error Rate: {subData.most_incorrect_question.error_rate}%</span>
                </div>
                <p className="text-xs text-gray-300 font-semibold">{subData.most_incorrect_question.question_text}</p>
                <div className="text-[10px] text-gray-500 leading-relaxed border-t border-red-500/10 pt-2">
                  <span className="font-semibold block text-red-300">Common Typo:</span>
                  {subData.most_incorrect_question.common_mistake}
                </div>
              </div>
            </div>

            <div className="mt-4 pt-4 border-t border-[#D4AF37]/5">
              <span className="text-[10px] text-gray-500 uppercase tracking-wider font-semibold">Faculty Insight</span>
              <p className="text-xs text-gray-300 italic mt-1 leading-normal">"{subData.faculty_insights}"</p>
            </div>
          </div>
        </div>
      )}

      {tab === 'reports' && (
        <div className="glass-card p-6 rounded-2xl text-center py-16 text-gray-400 space-y-2">
          <FileText className="w-12 h-12 text-gold mx-auto animate-pulse" />
          <h3 className="text-lg font-bold text-white">Generate Department Marks Matrix</h3>
          <p className="text-sm text-gray-500 max-w-sm mx-auto">Export departmental grading ledgers to Excel tables or download institution statistics.</p>
        </div>
      )}
    </div>
  );
}

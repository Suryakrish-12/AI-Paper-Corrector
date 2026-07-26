"use client";

import { useState, useEffect } from 'react';
import { useSearchParams } from 'next/navigation';
import { api } from '@/lib/api';
import { useAuthStore } from '@/store/useAuthStore';
import { 
  Award, TrendingUp, Sparkles, AlertCircle, BookOpen, 
  FileText, Download, CheckCircle, HelpCircle, Activity 
} from 'lucide-react';
import { 
  ResponsiveContainer, LineChart, Line, XAxis, YAxis, 
  Tooltip, CartesianGrid, BarChart, Bar, RadarChart, 
  PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar 
} from 'recharts';

export default function StudentDashboard() {
  const searchParams = useSearchParams();
  const tab = searchParams.get('tab') || 'overview';
  const { user } = useAuthStore();
  
  const [analyticsData, setAnalyticsData] = useState<any>(null);
  const [studentScripts, setStudentScripts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Fetch student analytics
    const fetchStudentData = async () => {
      try {
        setLoading(true);
        const studentId = user?.student_id || 1;

        const analyticsRes = await api.get(`/analytics/student/${studentId}`);
        setAnalyticsData(analyticsRes.data);
        
        // Find evaluated scripts for this student
        const scriptsRes = await api.get('/evaluation/answer-scripts');
        const matchedScripts = scriptsRes.data.filter(
          (s: any) => s.student_id === studentId && s.status === 'COMPLETED'
        );
        setStudentScripts(matchedScripts);
      } catch (err) {
        console.error("Error retrieving student dashboard analytics:", err);
      } finally {
        setLoading(false);
      }
    };
    
    if (user) {
      fetchStudentData();
    }
  }, [user]);

  if (loading || !analyticsData) {
    return (
      <div className="flex items-center justify-center py-24">
        <div className="w-10 h-10 border-2 border-[#D4AF37]/20 border-t-[#D4AF37] rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Dashboard Brand Title */}
      <div className="flex items-center justify-between border-b border-[#D4AF37]/10 pb-4">
        <div>
          <h1 className="text-3xl font-bold text-white leading-tight">My Academic Portal</h1>
          <p className="text-xs text-gray-500 mt-1">Review AI grading marks and descriptive feedback insights.</p>
        </div>
      </div>

      {tab === 'overview' && (
        <div className="space-y-8">
          {/* Quick Metrics Bar */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="glass-card p-5 rounded-xl flex items-center space-x-4">
              <div className="bg-[#D4AF37]/10 p-3 rounded-lg border border-[#D4AF37]/20 text-[#D4AF37]">
                <Award className="w-6 h-6" />
              </div>
              <div>
                <h4 className="text-gray-400 text-xs uppercase tracking-wider font-semibold">Average Score</h4>
                <p className="text-2xl font-bold text-white mt-1">{analyticsData.student_average}%</p>
              </div>
            </div>
            
            <div className="glass-card p-5 rounded-xl flex items-center space-x-4">
              <div className="bg-[#D4AF37]/10 p-3 rounded-lg border border-[#D4AF37]/20 text-[#D4AF37]">
                <TrendingUp className="w-6 h-6" />
              </div>
              <div>
                <h4 className="text-gray-400 text-xs uppercase tracking-wider font-semibold">Class Median</h4>
                <p className="text-2xl font-bold text-white mt-1">{analyticsData.class_average}%</p>
              </div>
            </div>

            <div className="glass-card p-5 rounded-xl flex items-center space-x-4">
              <div className="bg-[#D4AF37]/10 p-3 rounded-lg border border-[#D4AF37]/20 text-[#D4AF37]">
                <Activity className="w-6 h-6" />
              </div>
              <div>
                <h4 className="text-gray-400 text-xs uppercase tracking-wider font-semibold">Class Rank</h4>
                <p className="text-2xl font-bold text-gold mt-1">#{analyticsData.rank}</p>
              </div>
            </div>

            <div className="glass-card p-5 rounded-xl flex items-center space-x-4">
              <div className="bg-[#D4AF37]/10 p-3 rounded-lg border border-[#D4AF37]/20 text-[#D4AF37]">
                <BookOpen className="w-6 h-6" />
              </div>
              <div>
                <h4 className="text-gray-400 text-xs uppercase tracking-wider font-semibold">Exams Graded</h4>
                <p className="text-2xl font-bold text-white mt-1">{studentScripts.length || 1}</p>
              </div>
            </div>
          </div>

          {/* Radar & Line Charts row */}
          <div className="grid md:grid-cols-12 gap-6">
            {/* Concept Mastery Radar */}
            <div className="md:col-span-5 glass-card p-6 rounded-2xl">
              <h3 className="text-md font-semibold text-white mb-4">Topic Mastery Matrix</h3>
              <div className="h-64 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <RadarChart cx="50%" cy="50%" outerRadius="80%" data={analyticsData.topic_mastery}>
                    <PolarGrid stroke="#333" />
                    <PolarAngleAxis dataKey="topic" stroke="#888" fontSize={9} />
                    <PolarRadiusAxis stroke="#333" angle={30} domain={[0, 100]} />
                    <Radar name="My Mastery" dataKey="mastery" stroke="#D4AF37" fill="#D4AF37" fillOpacity={0.25} />
                  </RadarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Performance Trend Line chart */}
            <div className="md:col-span-7 glass-card p-6 rounded-2xl">
              <h3 className="text-md font-semibold text-white mb-4">Exam Performance Trend</h3>
              <div className="h-64 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={analyticsData.performance_history}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#222" />
                    <XAxis dataKey="exam" stroke="#666" fontSize={10} />
                    <YAxis stroke="#666" domain={[0, 100]} fontSize={10} />
                    <Tooltip contentStyle={{ backgroundColor: '#18181B', border: '1px solid #D4AF37' }} />
                    <Line type="monotone" dataKey="marks" stroke="#D4AF37" strokeWidth={2} dot={{ fill: '#D4AF37', r: 4 }} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>

          {/* Concept Strengths / Weaknesses listing */}
          <div className="grid md:grid-cols-2 gap-6">
            <div className="glass-card p-6 rounded-2xl space-y-4">
              <h4 className="text-sm font-bold text-white uppercase tracking-wider flex items-center space-x-1.5">
                <Sparkles className="w-4 h-4 text-[#D4AF37]" />
                <span>Concept Strengths</span>
              </h4>
              <ul className="space-y-2 text-xs">
                {analyticsData.strengths.map((str: string, idx: number) => (
                  <li key={idx} className="flex items-center space-x-2 bg-green-500/5 border border-green-500/10 p-2.5 rounded-lg text-green-300">
                    <CheckCircle className="w-4 h-4 shrink-0" />
                    <span>{str}</span>
                  </li>
                ))}
              </ul>
            </div>

            <div className="glass-card p-6 rounded-2xl space-y-4">
              <h4 className="text-sm font-bold text-white uppercase tracking-wider flex items-center space-x-1.5">
                <AlertCircle className="w-4 h-4 text-[#D4AF37]" />
                <span>Areas to Review</span>
              </h4>
              <ul className="space-y-2 text-xs">
                {analyticsData.weaknesses.map((weak: string, idx: number) => (
                  <li key={idx} className="flex items-center space-x-2 bg-red-500/5 border border-red-500/10 p-2.5 rounded-lg text-red-300">
                    <AlertCircle className="w-4 h-4 shrink-0" />
                    <span>{weak}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}

      {tab === 'concepts' && (
        <div className="glass-card p-6 rounded-2xl">
          <h3 className="text-lg font-semibold text-white mb-4">Topic Master Details</h3>
          <div className="h-80 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={analyticsData.topic_mastery}>
                <CartesianGrid strokeDasharray="3 3" stroke="#222" />
                <XAxis dataKey="topic" stroke="#666" fontSize={10} />
                <YAxis stroke="#666" domain={[0, 100]} fontSize={10} />
                <Tooltip contentStyle={{ backgroundColor: '#18181B', border: '1px solid #D4AF37' }} />
                <Bar dataKey="mastery" fill="#D4AF37" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {tab === 'downloads' && (
        <div className="glass-card p-6 rounded-2xl">
          <h3 className="text-lg font-semibold text-white mb-4">Graded Evaluation Reports</h3>
          
          {studentScripts.length === 0 ? (
            <div className="text-center py-12 text-gray-500 text-sm">
              Your exam submissions are currently in evaluation queue. Check back shortly.
            </div>
          ) : (
            <div className="space-y-3">
              {studentScripts.map((script: any) => (
                <div key={script.id} className="flex items-center justify-between bg-[#121214]/50 border border-gray-800 p-4 rounded-xl">
                  <div className="flex items-center space-x-3">
                    <FileText className="w-8 h-8 text-[#D4AF37]" />
                    <div>
                      <h4 className="text-white text-sm font-semibold">Script #{script.id} - Exam Paper Result</h4>
                      <p className="text-[10px] text-gray-500">Graded: {new Date(script.created_at).toLocaleDateString()}</p>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-6">
                    <div className="text-right">
                      <div className="text-white text-sm font-bold">{script.overall_marks} Points</div>
                      <div className="text-[10px] text-gray-400">{script.overall_percentage}% Grade</div>
                    </div>
                    
                    <a
                      href={`http://localhost:8000/api/reports/student-pdf/${script.id}`}
                      target="_blank"
                      className="bg-gradient-to-r from-[#D4AF37] to-[#AA7C11] hover:from-[#E5C158] hover:to-[#B88D1B] text-black font-semibold text-xs py-2 px-3 rounded flex items-center space-x-1.5 transition-all"
                    >
                      <Download className="w-3.5 h-3.5" />
                      <span>Download PDF</span>
                    </a>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

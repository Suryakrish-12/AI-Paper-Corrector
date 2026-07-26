"use client";

import { useState, useEffect } from 'react';
import { useSearchParams } from 'next/navigation';
import { useEvaluationStore, AnswerScript } from '@/store/useEvaluationStore';
import { api } from '@/lib/api';
import Link from 'next/link';
import { 
  UploadCloud, FileText, CheckCircle2, AlertTriangle, 
  HelpCircle, Settings2, Sparkles, BookOpen, Clock, 
  Award, PlayCircle, Eye, ArrowRight, Download
} from 'lucide-react';

export default function FacultyDashboard() {
  const searchParams = useSearchParams();
  const tab = searchParams.get('tab') || 'overview';
  
  const { 
    scripts, fetchScripts, uploadScripts, 
    liveProgresses, loading 
  } = useEvaluationStore();

  // QP creation form states
  const [examName, setExamName] = useState('Mid-Term Examination');
  const [academicYear, setAcademicYear] = useState('2025-2026');
  const [subjectCode, setSubjectCode] = useState('CS-302');
  const [maxMarks, setMaxMarks] = useState(40);
  const [questions, setQuestions] = useState([
    { question_number: '1', question_text: 'Define Stack and Queue. Explain their differences and give real-world applications.', max_marks: 10, model_answer: 'Stack is LIFO data structure. Queue is FIFO. Examples: Stack of plates, Queue at ticket counter.', keywords: ['LIFO', 'FIFO', 'plates', 'ticket'], mandatory_keywords: ['LIFO', 'FIFO'] },
    { question_number: '2', question_text: 'What is the difference between TCP and UDP? Explain with neat diagrams.', max_marks: 10, model_answer: 'TCP is connection-oriented, reliable, three-way handshake. UDP is connectionless, faster, streaming applications.', keywords: ['handshake', 'connectionless', 'reliable', 'sliding window'], mandatory_keywords: ['connection-oriented', 'connectionless'] },
    { question_number: '3', question_text: 'Implement binary search algorithm in Python/C. Explain its time complexity.', max_marks: 10, model_answer: 'Binary search is log(n) complexity. Sorted array checking. Pivot mid = (low + high) // 2.', keywords: ['binary', 'complexity', 'O(log n)', 'sorted'], mandatory_keywords: ['sorted', 'O(log n)'] },
    { question_number: '4', question_text: 'State Bayes Theorem. Solve: In a test, a patient tests positive for a disease with 99% accuracy. If the disease prevalence is 0.1%, what is the actual probability they have the disease?', max_marks: 10, model_answer: 'P(D|Pos) = P(Pos|D)*P(D) / P(Pos). Results in approximately 9.02% probability.', keywords: ['Bayes', 'prevalence', '9.02%', 'posterior'], mandatory_keywords: ['Bayes', '9.02'] }
  ]);

  // Upload script states
  const [qpId, setQpId] = useState<string>('');
  const [evalMode, setEvalMode] = useState<string>('STANDARD');
  const [uploadedFiles, setUploadedFiles] = useState<FileList | null>(null);
  const [customSettings, setCustomSettings] = useState({
    grammar_weight: 0.1,
    spelling_tolerance: 'moderate',
    semantic_similarity_threshold: 0.5,
    strictness_slider: 0.5
  });

  const [qpList, setQpList] = useState<any[]>([]);
  const [qpSuccess, setQpSuccess] = useState(false);
  const [uploadSuccess, setUploadSuccess] = useState(false);
  const [qpLoading, setQpLoading] = useState(false);

  const handleQPUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setQpLoading(true);
    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await api.post("/evaluation/upload-question-paper", formData, {
        headers: { "Content-Type": "multipart/form-data" }
      });
      const data = response.data;
      setExamName(data.exam_name);
      setAcademicYear(data.academic_year);
      setSubjectCode(data.subject_code);
      setMaxMarks(data.max_marks);
      setQuestions(data.questions);
      alert("AI Scan Complete! Rubric fields successfully populated from the uploaded Question Paper.");
    } catch (err) {
      console.error(err);
      alert("Failed to extract questions. Please check the file format or enter details manually.");
    } finally {
      setQpLoading(false);
    }
  };

  useEffect(() => {
    fetchScripts();
    // Load Question Papers
    api.get('/evaluation/question-papers').then(res => {
      setQpList(res.data);
      if (res.data.length > 0) setQpId(String(res.data[0].id));
    });
  }, [fetchScripts]);

  const handleCreateQP = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.post('/evaluation/question-papers', {
        exam_name: examName,
        academic_year: academicYear,
        subject_code: subjectCode,
        max_marks: maxMarks,
        passing_marks: maxMarks * 0.4,
        questions: questions
      });
      setQpSuccess(true);
      setTimeout(() => setQpSuccess(false), 3000);
      // Reload papers list
      const res = await api.get('/evaluation/question-papers');
      setQpList(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  const handleUploadSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!qpId || !uploadedFiles) return;
    
    const success = await uploadScripts(
      Number(qpId), 
      evalMode, 
      uploadedFiles, 
      evalMode === 'CUSTOM' ? customSettings : null
    );

    if (success) {
      setUploadSuccess(true);
      setUploadedFiles(null);
      setTimeout(() => setUploadSuccess(false), 3000);
    }
  };

  return (
    <div className="space-y-8">
      {/* Tab navigation headers */}
      <div className="flex items-center justify-between border-b border-[#D4AF37]/10 pb-4">
        <div>
          <h1 className="text-3xl font-bold text-white leading-tight">Evaluator Board</h1>
          <p className="text-xs text-gray-500 mt-1">Configure grading parameters and upload exam paper bundles.</p>
        </div>
      </div>

      {tab === 'overview' && (
        <div className="space-y-6">
          {/* Stats quick widgets */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="glass-card p-5 rounded-xl flex items-center space-x-4">
              <div className="bg-[#D4AF37]/10 p-3 rounded-lg border border-[#D4AF37]/20 text-[#D4AF37]">
                <FileText className="w-6 h-6" />
              </div>
              <div>
                <h4 className="text-gray-400 text-xs uppercase tracking-wider font-semibold">Total Scripts</h4>
                <p className="text-2xl font-bold text-white mt-1">{scripts.length}</p>
              </div>
            </div>
            
            <div className="glass-card p-5 rounded-xl flex items-center space-x-4">
              <div className="bg-green-500/10 p-3 rounded-lg border border-green-500/20 text-green-400">
                <CheckCircle2 className="w-6 h-6" />
              </div>
              <div>
                <h4 className="text-gray-400 text-xs uppercase tracking-wider font-semibold">Graded</h4>
                <p className="text-2xl font-bold text-white mt-1">
                  {scripts.filter(s => s.status === 'COMPLETED').length}
                </p>
              </div>
            </div>

            <div className="glass-card p-5 rounded-xl flex items-center space-x-4">
              <div className="bg-[#D4AF37]/10 p-3 rounded-lg border border-[#D4AF37]/20 text-[#D4AF37]">
                <Clock className="w-6 h-6 animate-pulse" />
              </div>
              <div>
                <h4 className="text-gray-400 text-xs uppercase tracking-wider font-semibold">Evaluating</h4>
                <p className="text-2xl font-bold text-white mt-1">
                  {scripts.filter(s => s.status !== 'COMPLETED' && s.status !== 'ERROR').length}
                </p>
              </div>
            </div>

            <div className="glass-card p-5 rounded-xl flex items-center space-x-4">
              <div className="bg-red-500/10 p-3 rounded-lg border border-red-500/20 text-red-400">
                <AlertTriangle className="w-6 h-6" />
              </div>
              <div>
                <h4 className="text-gray-400 text-xs uppercase tracking-wider font-semibold">Exceptions</h4>
                <p className="text-2xl font-bold text-white mt-1">
                  {scripts.filter(s => s.status === 'ERROR').length}
                </p>
              </div>
            </div>
          </div>

          {/* Active queue list */}
          <div className="glass-card p-6 rounded-2xl">
            <h3 className="text-lg font-semibold text-white mb-4">Grading Queue & Live Pipelines</h3>
            
            <div className="overflow-x-auto">
              {scripts.length === 0 ? (
                <div className="text-center py-12 text-gray-500 text-sm">
                  No answer scripts found. Navigate to "Upload Scripts" to submit sheets.
                </div>
              ) : (
                <table className="custom-table text-sm">
                  <thead>
                    <tr className="text-gray-500 text-xs uppercase tracking-wider">
                      <th className="text-left font-semibold">ID</th>
                      <th className="text-left font-semibold">Student Name</th>
                      <th className="text-center font-semibold">Pages</th>
                      <th className="text-center font-semibold">Mode</th>
                      <th className="text-center font-semibold">Score</th>
                      <th className="text-center font-semibold">Pipeline Status</th>
                      <th className="text-center font-semibold">Confidence</th>
                      <th className="text-center font-semibold">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {scripts.map((script) => {
                      const live = liveProgresses[script.id];
                      const activeStatus = live ? live.status : script.status;
                      const progress = live ? live.progress : (activeStatus === 'COMPLETED' ? 100 : 0);
                      
                      return (
                        <tr key={script.id} className="border-b border-[#D4AF37]/5">
                          <td className="font-semibold text-gray-300">#{script.id}</td>
                          <td>
                            <div>
                              <div className="font-semibold text-white">{script.student_name || "Anonymous Student"}</div>
                              <div className="text-[10px] text-gray-500">{script.register_number || "Evaluating..."}</div>
                            </div>
                          </td>
                          <td className="text-center text-gray-300">{script.total_pages || 2}</td>
                          <td className="text-center">
                            <span className="bg-[#121214] border border-[#D4AF37]/20 px-2 py-0.5 rounded text-[10px] text-gray-300">
                              {script.evaluation_mode}
                            </span>
                          </td>
                          <td className="text-center font-bold text-white">
                            {activeStatus === 'COMPLETED' && script.overall_marks !== null ? (
                              <span>{script.overall_marks} <span className="text-gray-500 font-normal">pts</span></span>
                            ) : (
                              <span className="text-gray-600">—</span>
                            )}
                          </td>
                          <td className="text-center px-4 w-48">
                            {activeStatus === 'COMPLETED' ? (
                              <span className="inline-flex items-center space-x-1 text-green-400 text-xs font-semibold">
                                <CheckCircle2 className="w-3.5 h-3.5" />
                                <span>Complete</span>
                              </span>
                            ) : activeStatus === 'ERROR' ? (
                              <span className="inline-flex items-center space-x-1 text-red-400 text-xs font-semibold">
                                <AlertTriangle className="w-3.5 h-3.5" />
                                <span>Failed</span>
                              </span>
                            ) : (
                              <div className="space-y-1">
                                <div className="flex justify-between text-[10px] text-gray-400">
                                  <span className="font-semibold uppercase text-gold">{activeStatus}</span>
                                  <span>{progress}%</span>
                                </div>
                                <div className="w-full bg-[#18181b] rounded-full h-1">
                                  <div 
                                    className="bg-gradient-to-r from-[#D4AF37] to-[#AA7C11] h-1 rounded-full transition-all duration-300"
                                    style={{ width: `${progress}%` }}
                                  />
                                </div>
                              </div>
                            )}
                          </td>
                          <td className="text-center font-medium text-gray-300">
                            {activeStatus === 'COMPLETED' ? `${Math.round(script.confidence_score * 100)}%` : '—'}
                          </td>
                          <td className="text-center">
                            <div className="flex items-center justify-center space-x-2">
                              {activeStatus === 'COMPLETED' ? (
                                <>
                                  <Link
                                    href={`/evaluation/${script.id}`}
                                    className="bg-[#D4AF37]/10 hover:bg-[#D4AF37]/20 border border-[#D4AF37]/35 text-[#D4AF37] p-1.5 rounded text-xs transition-all flex items-center space-x-1"
                                  >
                                    <Eye className="w-3.5 h-3.5" />
                                    <span>Verify</span>
                                  </Link>
                                  <a
                                    href={`http://localhost:8000/api/reports/student-pdf/${script.id}`}
                                    target="_blank"
                                    className="bg-[#121214] hover:bg-[#18181b] border border-gray-800 text-gray-300 p-1.5 rounded transition-all"
                                    title="Download PDF Report"
                                  >
                                    <Download className="w-3.5 h-3.5" />
                                  </a>
                                </>
                              ) : (
                                <button className="opacity-50 cursor-not-allowed bg-gray-800 border border-gray-700 text-gray-500 p-1.5 rounded text-xs">
                                  Running
                                </button>
                              )}
                            </div>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              )}
            </div>
          </div>
        </div>
      )}

      {tab === 'rubric' && (
        <div className="glass-card p-8 rounded-2xl max-w-3xl mx-auto">
          <h3 className="text-xl font-bold text-white mb-2 flex items-center space-x-2">
            <BookOpen className="text-[#D4AF37] w-5 h-5" />
            <span>Create Exam Schema & Rubrics</span>
          </h3>
          <p className="text-xs text-gray-500 mb-6">Map questions, model answers, and mandatory keyword rubrics for student evaluations.</p>

          {qpSuccess && (
            <div className="bg-green-500/10 border border-green-500/30 text-green-400 p-3 rounded-lg flex items-center space-x-2 text-xs mb-6">
              <CheckCircle2 className="w-4 h-4 shrink-0" />
              <span>Exam Question Paper created and registered successfully!</span>
            </div>
          )}

          <form onSubmit={handleCreateQP} className="space-y-6">
            {/* AI Auto-populate Dropzone */}
            <div className="bg-[#121214]/60 border border-[#D4AF37]/20 p-5 rounded-xl space-y-3">
              <span className="block text-xs font-bold text-white uppercase tracking-wider">AI Question Paper Parser (Optional)</span>
              <p className="text-[10px] text-gray-400 leading-normal">
                Upload the official question paper PDF/Image to auto-extract the exam details, questions list, max marks, and default model answer rubrics using AI.
              </p>
              <div className="flex items-center gap-3">
                <input
                  type="file"
                  onChange={handleQPUpload}
                  className="hidden"
                  id="qp-file-upload"
                  accept=".pdf,.png,.jpg,.jpeg"
                />
                <label
                  htmlFor="qp-file-upload"
                  className="bg-[#D4AF37]/10 hover:bg-[#D4AF37]/20 border border-[#D4AF37]/35 text-[#D4AF37] px-4 py-2 rounded-lg text-xs font-semibold cursor-pointer transition-all flex items-center gap-2"
                >
                  <UploadCloud className="w-4 h-4" />
                  <span>Choose PDF / Image</span>
                </label>
                {qpLoading && <span className="text-xs text-[#D4AF37] animate-pulse font-medium">Running OCR & parsing layout...</span>}
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Exam Description</label>
                <input
                  type="text"
                  value={examName}
                  onChange={(e) => setExamName(e.target.value)}
                  className="w-full bg-[#121214] border border-[#D4AF37]/10 focus:border-[#D4AF37]/40 rounded-lg py-2 px-3 text-sm text-white outline-none"
                  required
                />
              </div>
              
              <div>
                <label className="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Academic Year</label>
                <input
                  type="text"
                  value={academicYear}
                  onChange={(e) => setAcademicYear(e.target.value)}
                  className="w-full bg-[#121214] border border-[#D4AF37]/10 focus:border-[#D4AF37]/40 rounded-lg py-2 px-3 text-sm text-white outline-none"
                  required
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Subject Code</label>
                <input
                  type="text"
                  value={subjectCode}
                  onChange={(e) => setSubjectCode(e.target.value)}
                  className="w-full bg-[#121214] border border-[#D4AF37]/10 focus:border-[#D4AF37]/40 rounded-lg py-2 px-3 text-sm text-white outline-none"
                  required
                />
              </div>
              
              <div>
                <label className="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Maximum Marks</label>
                <input
                  type="number"
                  value={maxMarks}
                  onChange={(e) => setMaxMarks(Number(e.target.value))}
                  className="w-full bg-[#121214] border border-[#D4AF37]/10 focus:border-[#D4AF37]/40 rounded-lg py-2 px-3 text-sm text-white outline-none"
                  required
                />
              </div>
            </div>

            <div className="space-y-4 pt-4 border-t border-[#D4AF37]/10">
              <h4 className="text-sm font-semibold text-white">Questions list ({questions.length})</h4>
              
              {questions.map((q, idx) => (
                <div key={idx} className="bg-[#121214]/50 border border-gray-800 p-4 rounded-xl space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-[#D4AF37]">Question #{q.question_number}</span>
                    <span className="text-xs text-gray-400">{q.max_marks} Marks</span>
                  </div>
                  <div>
                    <span className="block text-[10px] text-gray-500 mb-1">Question Text:</span>
                    <p className="text-xs text-gray-300">{q.question_text}</p>
                  </div>
                  <div>
                    <span className="block text-[10px] text-gray-500 mb-1">Model Answer:</span>
                    <p className="text-xs text-gray-400 italic bg-[#0a0a0c] p-2 rounded">{q.model_answer}</p>
                  </div>
                </div>
              ))}
            </div>

            <button
              type="submit"
              className="w-full bg-gradient-to-r from-[#D4AF37] to-[#AA7C11] hover:from-[#E5C158] hover:to-[#B88D1B] text-black font-semibold text-sm py-2.5 rounded-lg transition-all cursor-pointer text-center"
            >
              Register Question Paper Schema
            </button>
          </form>
        </div>
      )}

      {tab === 'upload' && (
        <div className="grid md:grid-cols-12 gap-8 items-start">
          {/* Left panel: Upload settings and file drag area */}
          <div className="md:col-span-8 space-y-6">
            <div className="glass-card p-6 rounded-2xl">
              <h3 className="text-lg font-semibold text-white mb-2 flex items-center space-x-2">
                <UploadCloud className="text-[#D4AF37] w-5 h-5" />
                <span>Upload Student Answer Sheets</span>
              </h3>
              <p className="text-xs text-gray-500 mb-6">Select the target Exam Schema and upload single PDFs, images, or compressed ZIP bundles.</p>

              {uploadSuccess && (
                <div className="bg-green-500/10 border border-green-500/30 text-green-400 p-3 rounded-lg flex items-center space-x-2 text-xs mb-6">
                  <CheckCircle2 className="w-4 h-4 shrink-0" />
                  <span>Submissions uploaded successfully! Evaluator pipeline initiated.</span>
                </div>
              )}

              <form onSubmit={handleUploadSubmit} className="space-y-6">
                <div>
                  <label className="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Select Examination Scheme</label>
                  <select
                    value={qpId}
                    onChange={(e) => setQpId(e.target.value)}
                    className="w-full bg-[#121214] border border-[#D4AF37]/10 focus:border-[#D4AF37]/40 rounded-lg py-2.5 px-3 text-sm text-white outline-none cursor-pointer"
                    required
                  >
                    <option value="" disabled>Select active paper...</option>
                    {qpList.map(qp => (
                      <option key={qp.id} value={qp.id}>{qp.exam_name} ({qp.subject_id}) - {qp.academic_year}</option>
                    ))}
                  </select>
                </div>

                {/* Mode Select */}
                <div>
                  <label className="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">AI Evaluation Mode</label>
                  <div className="grid grid-cols-4 gap-2">
                    {[
                      { value: 'LIBERAL', label: 'Liberal', desc: 'High partial marks, soft spelling checks' },
                      { value: 'STANDARD', label: 'Standard', desc: 'Balanced university grading rules' },
                      { value: 'STRICT', label: 'Strict', desc: 'Verbatim keywords required, no padding' },
                      { value: 'CUSTOM', label: 'Custom', desc: 'Configure specific weights manually' }
                    ].map(mode => (
                      <button
                        key={mode.value}
                        type="button"
                        onClick={() => setEvalMode(mode.value)}
                        className={`p-3 rounded-lg text-left border transition-all cursor-pointer ${
                          evalMode === mode.value
                            ? 'bg-[#D4AF37]/15 border-[#D4AF37] text-white'
                            : 'bg-[#121214] border-transparent text-gray-400 hover:border-gray-800'
                        }`}
                      >
                        <h4 className="text-xs font-bold">{mode.label}</h4>
                        <p className="text-[9px] text-gray-500 mt-1 leading-tight">{mode.desc}</p>
                      </button>
                    ))}
                  </div>
                </div>

                {/* Custom Weights Configuration Accordion */}
                {evalMode === 'CUSTOM' && (
                  <div className="bg-[#121214]/40 border border-[#D4AF37]/10 p-5 rounded-xl space-y-4 animate-fadeIn">
                    <h4 className="text-xs font-semibold text-white flex items-center space-x-1.5 uppercase tracking-wider">
                      <Settings2 className="w-3.5 h-3.5 text-gold" />
                      <span>Custom Strictness Parameters</span>
                    </h4>
                    
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-[10px] text-gray-400 mb-1">Grammar Deductions Weight: {Math.round(customSettings.grammar_weight * 100)}%</label>
                        <input
                          type="range"
                          min="0"
                          max="0.5"
                          step="0.05"
                          value={customSettings.grammar_weight}
                          onChange={(e) => setCustomSettings({...customSettings, grammar_weight: Number(e.target.value)})}
                          className="w-full accent-gold cursor-pointer"
                        />
                      </div>
                      
                      <div>
                        <label className="block text-[10px] text-gray-400 mb-1">Spelling Tolerance</label>
                        <select
                          value={customSettings.spelling_tolerance}
                          onChange={(e) => setCustomSettings({...customSettings, spelling_tolerance: e.target.value})}
                          className="w-full bg-[#121214] border border-gray-800 rounded py-1 px-2 text-xs text-white"
                        >
                          <option value="none">Strict (Zero spelling drift)</option>
                          <option value="moderate">Moderate (Accept common variants)</option>
                          <option value="high">High (Ignore minor spelling typos)</option>
                        </select>
                      </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-[10px] text-gray-400 mb-1">Semantic Threshold: {customSettings.semantic_similarity_threshold}</label>
                        <input
                          type="range"
                          min="0.3"
                          max="0.9"
                          step="0.05"
                          value={customSettings.semantic_similarity_threshold}
                          onChange={(e) => setCustomSettings({...customSettings, semantic_similarity_threshold: Number(e.target.value)})}
                          className="w-full accent-gold cursor-pointer"
                        />
                      </div>
                      
                      <div>
                        <label className="block text-[10px] text-gray-400 mb-1">Strictness Factor: {customSettings.strictness_slider}</label>
                        <input
                          type="range"
                          min="0"
                          max="1.0"
                          step="0.1"
                          value={customSettings.strictness_slider}
                          onChange={(e) => setCustomSettings({...customSettings, strictness_slider: Number(e.target.value)})}
                          className="w-full accent-gold cursor-pointer"
                        />
                      </div>
                    </div>
                  </div>
                )}

                {/* Upload drag area */}
                <div className="border border-dashed border-[#D4AF37]/25 hover:border-[#D4AF37]/50 bg-[#121214]/20 hover:bg-[#121214]/30 rounded-xl p-8 text-center transition-all cursor-pointer relative">
                  <input
                    type="file"
                    onChange={(e) => setUploadedFiles(e.target.files)}
                    multiple
                    className="absolute inset-0 opacity-0 cursor-pointer"
                    required
                  />
                  <div className="space-y-2">
                    <UploadCloud className="w-10 h-10 text-[#D4AF37] mx-auto animate-bounce" />
                    <div className="text-sm font-semibold text-white">
                      {uploadedFiles ? `${uploadedFiles.length} file(s) selected` : 'Drag and drop files here, or click to browse'}
                    </div>
                    <p className="text-[10px] text-gray-500">Supports PDF, PNG, JPG, JPEG, and bulk ZIP bundles.</p>
                  </div>
                </div>

                <button
                  type="submit"
                  className="w-full bg-gradient-to-r from-[#D4AF37] to-[#AA7C11] hover:from-[#E5C158] hover:to-[#B88D1B] text-black font-semibold text-sm py-2.5 rounded-lg transition-all cursor-pointer text-center"
                >
                  Initiate AI Evaluator Pipeline
                </button>
              </form>
            </div>
          </div>

          {/* Right panel: Evaluation guidelines */}
          <div className="md:col-span-4 space-y-6">
            <div className="glass-card p-6 rounded-2xl">
              <h4 className="text-sm font-bold text-white mb-3 flex items-center space-x-1.5 uppercase tracking-wider">
                <Sparkles className="w-4 h-4 text-gold" />
                <span>Evaluation Pipeline Steps</span>
              </h4>
              <div className="space-y-4">
                {[
                  { step: '1. OCR Engine', desc: 'Layout parser extracts text coordinates and handwritten characters.' },
                  { step: '2. Subject Auto-detect', desc: 'Examines headings and pairs registration numbers to enrollment sheets.' },
                  { step: '3. Rubric Matcher', desc: 'Compares responses against key terms and model formulas.' },
                  { step: '4. Generative Grading', desc: 'Runs LLM scoring against selected strictness parameters.' },
                  { step: '5. AI Breakdown', desc: 'Generates final markings summary and missing concept recommendations.' }
                ].map((s, idx) => (
                  <div key={idx} className="flex items-start space-x-3 text-xs">
                    <span className="w-5 h-5 rounded-full bg-[#D4AF37]/10 text-gold flex items-center justify-center font-bold text-[10px] shrink-0 mt-0.5">{idx + 1}</span>
                    <div>
                      <h5 className="font-semibold text-white">{s.step}</h5>
                      <p className="text-gray-500 mt-0.5 leading-normal">{s.desc}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {tab === 'analytics' && (
        <div className="glass-card p-6 rounded-2xl text-center py-16 text-gray-400 space-y-2">
          <Award className="w-12 h-12 text-gold mx-auto" />
          <h3 className="text-lg font-bold text-white">Faculty Insights</h3>
          <p className="text-sm text-gray-500 max-w-md mx-auto">Detailed subject and incorrect question matrices. Access the HOD portal for institution-wide comparisons.</p>
        </div>
      )}
    </div>
  );
}

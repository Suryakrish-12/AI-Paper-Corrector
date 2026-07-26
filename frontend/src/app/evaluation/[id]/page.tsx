"use client";

import { use, useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useEvaluationStore, EvaluationItem } from '@/store/useEvaluationStore';
import { 
  ArrowLeft, Check, AlertCircle, Save, CheckCircle2, 
  HelpCircle, Eye, ShieldAlert, Sparkles, BookOpen 
} from 'lucide-react';
import Link from 'next/link';

export default function EvaluationDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const router = useRouter();
  const { id } = use(params);
  const scriptId = Number(id);

  const { 
    currentScript, currentEvaluations, fetchScriptDetails, 
    overrideMarks, approveScript, loading 
  } = useEvaluationStore();

  // Form states for edits
  const [activeEvalId, setActiveEvalId] = useState<number | null>(null);
  const [overrideValue, setOverrideValue] = useState<string>('');
  const [overrideNotes, setOverrideNotes] = useState<string>('');
  
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [approveSuccess, setApproveSuccess] = useState(false);

  useEffect(() => {
    fetchScriptDetails(scriptId);
  }, [scriptId, fetchScriptDetails]);

  const handleOpenOverride = (item: EvaluationItem) => {
    setActiveEvalId(item.id);
    setOverrideValue(String(item.teacher_override_marks !== null ? item.teacher_override_marks : item.marks_awarded));
    setOverrideNotes(item.teacher_notes || '');
  };

  const handleSaveOverride = async (e: React.FormEvent, evalId: number) => {
    e.preventDefault();
    const marks = Number(overrideValue);
    if (isNaN(marks) || marks < 0) return;

    const success = await overrideMarks(evalId, marks, overrideNotes);
    if (success) {
      setSaveSuccess(true);
      setActiveEvalId(null);
      setTimeout(() => setSaveSuccess(false), 2500);
    }
  };

  const handleApproveScript = async () => {
    const success = await approveScript(scriptId);
    if (success) {
      setApproveSuccess(true);
      setTimeout(() => {
        setApproveSuccess(false);
        router.push('/dashboard/faculty');
      }, 2000);
    }
  };

  if (loading || !currentScript) {
    return (
      <div className="min-h-screen bg-[#070708] flex items-center justify-center">
        <div className="w-10 h-10 border-2 border-[#D4AF37]/20 border-t-[#D4AF37] rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#070708] text-gray-100 p-8 space-y-6">
      
      {/* Header section with back navigation */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-[#D4AF37]/10 pb-6">
        <div className="flex items-center space-x-4">
          <Link
            href="/dashboard/faculty"
            className="p-2 bg-[#121214] border border-[#D4AF37]/10 hover:border-[#D4AF37]/30 text-gray-300 hover:text-white rounded-lg transition-all"
          >
            <ArrowLeft className="w-4 h-4" />
          </Link>
          <div>
            <div className="flex items-center space-x-2">
              <h1 className="text-2xl font-bold text-white">Grading Audit: #{currentScript.id}</h1>
              <span className="bg-[#D4AF37]/10 border border-[#D4AF37]/25 text-[#D4AF37] text-[10px] font-bold px-2 py-0.5 rounded uppercase">
                {currentScript.evaluation_mode}
              </span>
            </div>
            <p className="text-xs text-gray-500 mt-1">
              Student: <span className="text-gray-300 font-semibold">{currentScript.student_name}</span> ({currentScript.register_number})
            </p>
          </div>
        </div>

        {/* Global actions */}
        <div className="flex items-center space-x-3">
          <div className="bg-[#121214]/60 border border-[#D4AF37]/10 px-4 py-2 rounded-xl text-right">
            <span className="block text-[10px] text-gray-500 font-semibold uppercase">Aggregated Grade</span>
            <span className="text-gold font-bold text-lg">{currentScript.overall_marks}</span>
            <span className="text-xs text-gray-400"> / 40.0 pts</span>
          </div>

          <button
            onClick={handleApproveScript}
            className="bg-gradient-to-r from-green-600 to-green-700 hover:from-green-500 hover:to-green-600 text-white font-semibold text-xs py-2 px-4 rounded-xl flex items-center space-x-1.5 transition-all cursor-pointer h-full"
          >
            <Check className="w-4 h-4" />
            <span>Approve Grading</span>
          </button>
        </div>
      </div>

      {approveSuccess && (
        <div className="bg-green-500/10 border border-green-500/30 text-green-400 p-4 rounded-xl flex items-center space-x-2 text-xs animate-fadeIn">
          <CheckCircle2 className="w-5 h-5 shrink-0" />
          <span>Grading approved successfully! Returning to Dashboard...</span>
        </div>
      )}

      {/* Main Review Workspace */}
      <div className="grid md:grid-cols-12 gap-8 items-start">
        
        {/* Left column: Scanned OCR Output */}
        <div className="md:col-span-5 space-y-4">
          <div className="glass-card p-5 rounded-2xl">
            <h3 className="text-sm font-bold text-white uppercase tracking-wider mb-3 flex items-center space-x-1.5">
              <Eye className="w-4 h-4 text-gold" />
              <span>OCR Layout Extracted Sheet</span>
            </h3>
            
            <div className="bg-[#0c0c0e] border border-gray-800 rounded-xl p-4 h-[550px] overflow-y-auto font-mono text-xs text-gray-400 leading-relaxed whitespace-pre-wrap select-text">
              {currentEvaluations.map((item, idx) => (
                <div key={idx} className="mb-6 pb-6 border-b border-gray-900 last:border-b-0">
                  <h4 className="text-[#D4AF37] font-semibold mb-2 uppercase tracking-wide">Answer {item.question_number}</h4>
                  <p className="italic bg-[#121214]/40 p-3 rounded border border-gray-800/20 text-gray-300">
                    "{item.student_answer_text || "[Answer script left blank for this question]"}"
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right column: AI Evaluations list & Correction Forms */}
        <div className="md:col-span-7 space-y-4">
          {currentEvaluations.map((item) => {
            const isEditing = activeEvalId === item.id;
            const hasOverride = item.teacher_override_marks !== null;
            const scoreDisplay = hasOverride ? item.teacher_override_marks : item.marks_awarded;

            return (
              <div 
                key={item.id} 
                className={`glass-card p-6 rounded-2xl transition-all border ${
                  isEditing ? 'border-[#D4AF37] shadow-lg shadow-[#D4AF37]/5' : 'border-[#D4AF37]/10'
                }`}
              >
                {/* Header row */}
                <div className="flex items-center justify-between mb-4 border-b border-[#D4AF37]/5 pb-3">
                  <div>
                    <h3 className="text-white text-sm font-bold">Question {item.question_number}</h3>
                    <p className="text-[10px] text-gray-500 mt-0.5 max-w-sm truncate">{item.question_text}</p>
                  </div>
                  
                  <div className="flex items-center space-x-4">
                    <div className="text-right">
                      <span className="block text-[9px] text-gray-500 font-semibold uppercase">Score</span>
                      <span className={`font-bold ${hasOverride ? 'text-gold' : 'text-white'}`}>
                        {scoreDisplay}
                      </span>
                      <span className="text-xs text-gray-500"> / {item.max_marks} pts</span>
                    </div>

                    {!isEditing && (
                      <button
                        onClick={() => handleOpenOverride(item)}
                        className="bg-[#121214] hover:bg-[#18181b] border border-gray-800 text-gray-300 px-2 py-1 rounded text-[10px] transition-all cursor-pointer uppercase tracking-wider font-semibold"
                      >
                        Correct Marks
                      </button>
                    )}
                  </div>
                </div>

                {/* Body Details */}
                <div className="space-y-4 text-xs">
                  <div>
                    <span className="block text-[10px] text-gray-500 font-semibold mb-1 uppercase tracking-wider">Evaluation Prompt</span>
                    <p className="text-gray-300 bg-[#0a0a0c] p-2.5 rounded border border-gray-800/10 leading-normal">{item.question_text}</p>
                  </div>

                  <div className="grid md:grid-cols-2 gap-4">
                    <div>
                      <span className="block text-[10px] text-gray-500 font-semibold mb-1 uppercase tracking-wider">AI Reasoning Explanation</span>
                      <p className="text-gray-400 italic leading-relaxed">{item.explanation}</p>
                    </div>
                    
                    <div className="space-y-3">
                      <div>
                        <span className="block text-[10px] text-gray-500 font-semibold mb-1 uppercase tracking-wider">Concept Validation Alerts</span>
                        <div className="flex flex-wrap gap-1.5 mt-1">
                          {item.missing_concepts && item.missing_concepts.length > 0 ? (
                            item.missing_concepts.map((concept, idx) => (
                              <span key={idx} className="bg-red-500/5 border border-red-500/15 text-red-400 text-[9px] font-medium px-2 py-0.5 rounded">
                                {concept}
                              </span>
                            ))
                          ) : (
                            <span className="bg-green-500/5 border border-green-500/15 text-green-400 text-[9px] font-medium px-2 py-0.5 rounded">
                              Satisfied all core requirements
                            </span>
                          )}
                        </div>
                      </div>

                      {/* Structural Features detected */}
                      <div className="flex space-x-3 text-[10px]">
                        <span className={`inline-block font-semibold px-2 py-0.5 rounded uppercase tracking-wider ${
                          item.diagram_detected 
                            ? 'bg-green-500/10 text-green-400 border border-green-500/20' 
                            : 'bg-gray-800 text-gray-500 border border-transparent'
                        }`}>
                          Diagram: {item.diagram_detected ? 'Detected' : 'Missing'}
                        </span>
                        
                        <span className={`inline-block font-semibold px-2 py-0.5 rounded uppercase tracking-wider ${
                          item.formula_detected 
                            ? 'bg-green-500/10 text-green-400 border border-green-500/20' 
                            : 'bg-gray-800 text-gray-500 border border-transparent'
                        }`}>
                          Math Formula: {item.formula_detected ? 'Detected' : 'Missing'}
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Override Mode panel */}
                  {isEditing && (
                    <form onSubmit={(e) => handleSaveOverride(e, item.id)} className="bg-[#121214]/60 border border-[#D4AF37]/25 p-4 rounded-xl space-y-4 animate-slideDown">
                      <h4 className="text-[10px] font-semibold text-gold uppercase tracking-wider flex items-center space-x-1.5">
                        <Sparkles className="w-3.5 h-3.5 text-gold" />
                        <span>Teacher Corrections Console</span>
                      </h4>

                      <div className="grid grid-cols-3 gap-4 items-center">
                        <div className="col-span-1">
                          <label className="block text-[10px] text-gray-500 mb-1 font-semibold uppercase tracking-wider">Override Score</label>
                          <input
                            type="number"
                            min="0"
                            max={item.max_marks}
                            step="0.5"
                            value={overrideValue}
                            onChange={(e) => setOverrideValue(e.target.value)}
                            className="w-full bg-[#0a0a0c] border border-gray-800 rounded px-2 py-1 text-sm text-white outline-none"
                            required
                          />
                        </div>
                        
                        <div className="col-span-2">
                          <label className="block text-[10px] text-gray-500 mb-1 font-semibold uppercase tracking-wider">Evaluator Remarks / Notes</label>
                          <input
                            type="text"
                            value={overrideNotes}
                            onChange={(e) => setOverrideNotes(e.target.value)}
                            placeholder="Add corrections rationale here..."
                            className="w-full bg-[#0a0a0c] border border-gray-800 rounded px-2 py-1 text-xs text-white outline-none"
                          />
                        </div>
                      </div>

                      <div className="flex items-center justify-end space-x-2">
                        <button
                          type="button"
                          onClick={() => setActiveEvalId(null)}
                          className="bg-transparent hover:bg-gray-800 border border-gray-800 text-gray-400 px-3 py-1 rounded text-[10px] font-semibold transition-all cursor-pointer"
                        >
                          Cancel
                        </button>
                        
                        <button
                          type="submit"
                          className="bg-gradient-to-r from-[#D4AF37] to-[#AA7C11] text-black px-3 py-1 rounded text-[10px] font-bold transition-all flex items-center space-x-1 cursor-pointer"
                        >
                          <Save className="w-3.5 h-3.5" />
                          <span>Save Marks Override</span>
                        </button>
                      </div>
                    </form>
                  )}

                  {/* Saved overrides indicators */}
                  {hasOverride && !isEditing && (
                    <div className="bg-[#D4AF37]/5 border border-[#D4AF37]/20 p-2.5 rounded-lg text-[10px] flex items-start space-x-2">
                      <Sparkles className="w-3.5 h-3.5 text-gold shrink-0 mt-0.5" />
                      <div>
                        <span className="font-semibold text-gold uppercase tracking-wider block">Teacher Override Note:</span>
                        <p className="text-gray-400 italic mt-0.5">"{item.teacher_notes || 'Marks corrected by reviewer.'}"</p>
                      </div>
                    </div>
                  )}

                </div>
              </div>
            );
          })}
        </div>

      </div>

    </div>
  );
}

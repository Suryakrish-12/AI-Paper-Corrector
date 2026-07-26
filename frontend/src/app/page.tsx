"use client";

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/store/useAuthStore';
import { Cpu, Mail, Lock, ShieldAlert, Award, FileSpreadsheet } from 'lucide-react';

export default function LoginPage() {
  const router = useRouter();
  const { login, user, loading, loadUser } = useAuthStore();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Initialize session on mount
  useEffect(() => {
    loadUser();
  }, [loadUser]);

  // Route once authenticated
  useEffect(() => {
    if (user) {
      if (user.role === 'SUPER_ADMIN' || user.role === 'ADMIN') {
        router.push('/dashboard/admin');
      } else if (user.role === 'HOD') {
        router.push('/dashboard/hod');
      } else if (user.role === 'FACULTY') {
        router.push('/dashboard/faculty');
      } else if (user.role === 'STUDENT') {
        router.push('/dashboard/student');
      }
    }
  }, [user, router]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !password) {
      setError('Please provide both credentials.');
      return;
    }

    setError('');
    setIsSubmitting(true);
    const success = await login(email, password);
    setIsSubmitting(false);

    if (!success) {
      setError('Invalid email or password. Please try again.');
    }
  };

  const prefillUser = (roleEmail: string) => {
    setEmail(roleEmail);
    setPassword('password123');
  };

  return (
    <div className="relative min-h-screen flex items-center justify-center bg-[#070708] overflow-hidden px-4">
      {/* Premium Background Ambient Golden Orbs */}
      <div className="absolute top-[-10%] left-[-10%] w-[50%] h-[50%] bg-[#D4AF37]/5 rounded-full filter blur-[120px] pointer-events-none" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[50%] h-[50%] bg-[#AA7C11]/5 rounded-full filter blur-[120px] pointer-events-none" />
      
      {/* Flowing Grid lines */}
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#8080800a_1px,transparent_1px),linear-gradient(to_bottom,#8080800a_1px,transparent_1px)] bg-[size:14px_24px] pointer-events-none" />

      <div className="relative w-full max-w-5xl grid md:grid-cols-12 gap-8 items-center z-10">
        
        {/* Left Side: System Marketing / Description */}
        <div className="md:col-span-7 space-y-6 text-left pr-4">
          <div className="inline-flex items-center space-x-2 bg-gradient-to-r from-[#D4AF37]/10 to-[#AA7C11]/10 border border-[#D4AF37]/20 px-3 py-1.5 rounded-full text-[#D4AF37] text-xs font-semibold uppercase tracking-wider">
            <Cpu className="w-3.5 h-3.5" />
            <span>AI-Powered Examination Grading</span>
          </div>
          
          <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold tracking-tight text-white leading-tight">
            SmartEval <span className="text-gold">AI</span>
          </h1>
          
          <p className="text-gray-400 text-base md:text-lg leading-relaxed max-w-xl">
            A production-ready Intelligent Examination Paper Evaluation and Learning Analytics System. Automatically grades descriptive answers, runs OCR layouts, matches rubrics, and yields explainable AI diagnostics.
          </p>

          {/* Core system highlights */}
          <div className="grid grid-cols-2 gap-4 pt-4">
            <div className="flex items-start space-x-3">
              <div className="bg-[#D4AF37]/10 p-2 rounded-lg border border-[#D4AF37]/10 text-[#D4AF37] mt-0.5">
                <Award className="w-4 h-4" />
              </div>
              <div>
                <h4 className="text-white text-sm font-semibold">Explainable Scoring</h4>
                <p className="text-xs text-gray-500">Provides rubric itemization & missing concept alerts.</p>
              </div>
            </div>
            
            <div className="flex items-start space-x-3">
              <div className="bg-[#D4AF37]/10 p-2 rounded-lg border border-[#D4AF37]/10 text-[#D4AF37] mt-0.5">
                <FileSpreadsheet className="w-4 h-4" />
              </div>
              <div>
                <h4 className="text-white text-sm font-semibold">Learning Analytics</h4>
                <p className="text-xs text-gray-500">Subject mastery and department performance matrices.</p>
              </div>
            </div>
          </div>
        </div>

        {/* Right Side: Login Panel */}
        <div className="md:col-span-5 w-full">
          <div className="glass-card p-8 rounded-2xl w-full max-w-md mx-auto">
            <div className="space-y-2 text-center mb-6">
              <h2 className="text-2xl font-bold text-white tracking-tight">Institutional Sign-In</h2>
              <p className="text-gray-400 text-xs">Access dashboards using credentials or select pre-seeded demo roles below.</p>
            </div>

            {error && (
              <div className="bg-red-500/10 border border-red-500/30 text-red-400 p-3 rounded-lg flex items-center space-x-2 text-xs mb-4">
                <ShieldAlert className="w-4 h-4 shrink-0" />
                <span>{error}</span>
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Email Address</label>
                <div className="relative">
                  <Mail className="absolute left-3 top-3 w-4 h-4 text-gray-500" />
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="name@institution.com"
                    className="w-full bg-[#121214] border border-[#D4AF37]/10 focus:border-[#D4AF37]/40 rounded-lg py-2.5 pl-10 pr-4 text-sm text-white placeholder-gray-600 outline-none transition-all"
                    required
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Password</label>
                <div className="relative">
                  <Lock className="absolute left-3 top-3 w-4 h-4 text-gray-500" />
                  <input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="••••••••"
                    className="w-full bg-[#121214] border border-[#D4AF37]/10 focus:border-[#D4AF37]/40 rounded-lg py-2.5 pl-10 pr-4 text-sm text-white placeholder-gray-600 outline-none transition-all"
                    required
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={isSubmitting}
                className="w-full bg-gradient-to-r from-[#D4AF37] to-[#AA7C11] hover:from-[#E5C158] hover:to-[#B88D1B] text-black font-semibold text-sm py-2.5 rounded-lg transition-all transform hover:scale-[1.01] active:scale-[0.99] disabled:opacity-50 cursor-pointer shadow-lg shadow-[#D4AF37]/10"
              >
                {isSubmitting ? 'Authenticating...' : 'Sign In'}
              </button>
            </form>

            {/* Seed Quick-login assistance for demo evaluation */}
            <div className="mt-8 pt-6 border-t border-[#D4AF37]/10">
              <p className="text-gray-400 text-xs font-semibold uppercase tracking-wider mb-3 text-center">Demo Quick Login</p>
              <div className="flex flex-col space-y-2">
                <button
                  onClick={() => prefillUser('admin@smarteval.ai')}
                  className="w-full flex items-center justify-between bg-[#121214]/60 hover:bg-[#121214] border border-[#D4AF37]/5 hover:border-[#D4AF37]/25 text-left text-xs py-2 px-3 rounded-lg text-gray-300 transition-all"
                >
                  <span>Institution Admin</span>
                  <span className="text-[10px] text-[#D4AF37] font-semibold">admin@smarteval.ai</span>
                </button>
                <button
                  onClick={() => prefillUser('faculty@smarteval.ai')}
                  className="w-full flex items-center justify-between bg-[#121214]/60 hover:bg-[#121214] border border-[#D4AF37]/5 hover:border-[#D4AF37]/25 text-left text-xs py-2 px-3 rounded-lg text-gray-300 transition-all"
                >
                  <span>Evaluator / Faculty</span>
                  <span className="text-[10px] text-[#D4AF37] font-semibold">faculty@smarteval.ai</span>
                </button>
                <button
                  onClick={() => prefillUser('student1@smarteval.ai')}
                  className="w-full flex items-center justify-between bg-[#121214]/60 hover:bg-[#121214] border border-[#D4AF37]/5 hover:border-[#D4AF37]/25 text-left text-xs py-2 px-3 rounded-lg text-gray-300 transition-all"
                >
                  <span>Student (Ananya)</span>
                  <span className="text-[10px] text-[#D4AF37] font-semibold">student1@smarteval.ai</span>
                </button>
              </div>
            </div>
            
          </div>
        </div>

      </div>
    </div>
  );
}

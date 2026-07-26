"use client";

import { useEffect, useState } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { useAuthStore } from '@/store/useAuthStore';
import { useEvaluationStore } from '@/store/useEvaluationStore';
import { 
  LayoutDashboard, BookOpen, Users, Award, FileText, 
  Settings, LogOut, UploadCloud, LineChart, Activity, 
  Building2, GraduationCap, ServerCrash
} from 'lucide-react';
import Link from 'next/link';

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();
  const pathname = usePathname();
  const { user, token, logout, loadUser, loading } = useAuthStore();
  const { connectWebSocket, disconnectWebSocket, wsConnected } = useEvaluationStore();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    loadUser();
  }, [loadUser]);

  // Connect WebSockets when authenticated
  useEffect(() => {
    if (token) {
      connectWebSocket();
    }
    return () => {
      disconnectWebSocket();
    };
  }, [token, connectWebSocket, disconnectWebSocket]);

  // Redirect if session is cleared
  useEffect(() => {
    if (mounted && !loading && !user) {
      router.push('/');
    }
  }, [user, loading, mounted, router]);

  // Route-guard: Redirect to correct dashboard on unauthorized URL paths
  useEffect(() => {
    if (mounted && user && pathname) {
      const role = user.role;
      const isAdminPath = pathname.includes('/dashboard/admin');
      const isHodPath = pathname.includes('/dashboard/hod');
      const isFacultyPath = pathname.includes('/dashboard/faculty');
      const isStudentPath = pathname.includes('/dashboard/student');

      if (isAdminPath && role !== 'ADMIN' && role !== 'SUPER_ADMIN') {
        const target = role === 'HOD' ? '/dashboard/hod' : role === 'FACULTY' ? '/dashboard/faculty' : '/dashboard/student';
        router.push(target);
      } else if (isHodPath && role !== 'HOD') {
        const target = role === 'ADMIN' || role === 'SUPER_ADMIN' ? '/dashboard/admin' : role === 'FACULTY' ? '/dashboard/faculty' : '/dashboard/student';
        router.push(target);
      } else if (isFacultyPath && role !== 'FACULTY') {
        const target = role === 'ADMIN' || role === 'SUPER_ADMIN' ? '/dashboard/admin' : role === 'HOD' ? '/dashboard/hod' : '/dashboard/student';
        router.push(target);
      } else if (isStudentPath && role !== 'STUDENT') {
        const target = role === 'ADMIN' || role === 'SUPER_ADMIN' ? '/dashboard/admin' : role === 'HOD' ? '/dashboard/hod' : '/dashboard/faculty';
        router.push(target);
      }
    }
  }, [user, pathname, mounted, router]);

  if (!mounted || loading || !user) {
    return (
      <div className="min-h-screen bg-[#070708] flex items-center justify-center">
        <div className="relative">
          <div className="w-12 h-12 border-2 border-[#D4AF37]/20 border-t-[#D4AF37] rounded-full animate-spin" />
        </div>
      </div>
    );
  }

  // Determine role-based navigation links
  const getNavLinks = () => {
    const role = user.role;
    
    if (role === 'SUPER_ADMIN' || role === 'ADMIN') {
      return [
        { label: 'Admin Metrics', href: '/dashboard/admin', icon: LayoutDashboard },
        { label: 'Departments', href: '/dashboard/admin?tab=departments', icon: Building2 },
        { label: 'Faculty Management', href: '/dashboard/admin?tab=faculty', icon: Users },
        { label: 'Student Management', href: '/dashboard/admin?tab=students', icon: GraduationCap },
        { label: 'Audit Log Files', href: '/dashboard/admin?tab=audit', icon: Activity },
      ];
    }
    
    if (role === 'HOD') {
      return [
        { label: 'HOD Overview', href: '/dashboard/hod', icon: LayoutDashboard },
        { label: 'Faculty Comparison', href: '/dashboard/hod?tab=faculty', icon: Users },
        { label: 'Subject Performance', href: '/dashboard/hod?tab=subjects', icon: BookOpen },
        { label: 'Department Reports', href: '/dashboard/hod?tab=reports', icon: FileText },
      ];
    }
    
    if (role === 'FACULTY') {
      return [
        { label: 'Evaluator Main', href: '/dashboard/faculty', icon: LayoutDashboard },
        { label: 'Create Exam Rubric', href: '/dashboard/faculty?tab=rubric', icon: BookOpen },
        { label: 'Upload Scripts', href: '/dashboard/faculty?tab=upload', icon: UploadCloud },
        { label: 'Analytics Insights', href: '/dashboard/faculty?tab=analytics', icon: LineChart },
      ];
    }
    
    // STUDENT
    return [
      { label: 'My Performance', href: '/dashboard/student', icon: Award },
      { label: 'Concept Strengths', href: '/dashboard/student?tab=concepts', icon: LineChart },
      { label: 'Reports Download', href: '/dashboard/student?tab=downloads', icon: FileText },
    ];
  };

  const links = getNavLinks();

  return (
    <div className="min-h-screen bg-[#070708] flex">
      {/* Sidebar Navigation */}
      <aside className="w-64 bg-[#0a0a0c] border-r border-[#D4AF37]/10 flex flex-col justify-between shrink-0">
        <div>
          {/* Logo Brand Header */}
          <div className="h-16 flex items-center px-6 border-b border-[#D4AF37]/5">
            <span className="text-xl font-bold tracking-wider text-white">
              SmartEval <span className="text-gold">AI</span>
            </span>
          </div>

          {/* User badge */}
          <div className="p-4 mx-3 my-4 bg-[#121214]/60 border border-[#D4AF37]/10 rounded-xl">
            <h4 className="text-white text-sm font-semibold truncate">{user.name}</h4>
            <p className="text-[10px] text-gray-500 truncate mb-2">{user.email}</p>
            <span className="inline-block bg-[#D4AF37]/15 border border-[#D4AF37]/35 text-[#D4AF37] text-[9px] font-bold px-2 py-0.5 rounded-full uppercase tracking-wider">
              {user.role.replace('_', ' ')}
            </span>
          </div>

          {/* Links list */}
          <nav className="px-3 space-y-1.5">
            {links.map((link, idx) => {
              const Icon = link.icon;
              return (
                <Link
                  key={idx}
                  href={link.href}
                  className={`flex items-center space-x-3 px-4 py-2.5 rounded-lg text-sm font-medium transition-all ${
                    pathname === link.href.split('?')[0]
                      ? 'bg-[#D4AF37]/15 text-[#D4AF37] border-l-2 border-[#D4AF37]'
                      : 'text-gray-400 hover:bg-[#121214] hover:text-white'
                  }`}
                >
                  <Icon className="w-4.5 h-4.5" />
                  <span>{link.label}</span>
                </Link>
              );
            })}
          </nav>
        </div>

        {/* Footer actions inside Sidebar */}
        <div className="p-4 border-t border-[#D4AF37]/5 space-y-3">
          {/* WebSocket Status Indicator */}
          <div className="flex items-center justify-between bg-[#121214]/40 px-3 py-1.5 rounded-lg border border-[#D4AF37]/5">
            <span className="text-[10px] text-gray-500 uppercase tracking-wider font-semibold">Live Connection</span>
            <div className="flex items-center space-x-1.5">
              <span className={`w-2 h-2 rounded-full ${wsConnected ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`} />
              <span className="text-[10px] text-white font-medium">{wsConnected ? 'Live' : 'Offline'}</span>
            </div>
          </div>

          <button
            onClick={() => logout()}
            className="w-full flex items-center space-x-3 px-4 py-2.5 text-gray-400 hover:bg-red-500/10 hover:text-red-400 rounded-lg text-sm font-medium transition-all cursor-pointer"
          >
            <LogOut className="w-4.5 h-4.5" />
            <span>Sign Out</span>
          </button>
        </div>
      </aside>

      {/* Main Workspace Frame */}
      <main className="flex-1 flex flex-col overflow-y-auto">
        <header className="h-16 border-b border-[#D4AF37]/5 flex items-center justify-between px-8 bg-[#070708]/80 backdrop-blur-md sticky top-0 z-30">
          <div>
            <h2 className="text-white text-md font-semibold">
              {pathname.includes('admin') ? 'Administration Console' : 
               pathname.includes('faculty') ? 'Evaluator Board' : 
               pathname.includes('hod') ? 'Academic Oversight' : 'Student Report Dashboard'}
            </h2>
          </div>
          
          <div className="flex items-center space-x-4">
            <span className="text-xs text-gray-500 font-medium">Academic Year: 2025 - 2026</span>
          </div>
        </header>

        {/* Dynamic page content */}
        <div className="p-8 max-w-7xl w-full mx-auto flex-1">
          {children}
        </div>
      </main>
    </div>
  );
}

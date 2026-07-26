import { create } from 'zustand';
import { api } from '@/lib/api';

export interface AnswerScript {
  id: number;
  student_id: number | null;
  student_name: string;
  register_number: string;
  question_paper_id: number;
  file_path: string;
  status: string; // UPLOADING, OCR, QUESTION_DETECTION, SEMANTIC, EVALUATING, COMPLETED, ERROR
  is_handwritten: boolean;
  total_pages: number;
  file_type: string;
  evaluation_mode: string;
  overall_marks: number | null;
  overall_percentage: number | null;
  ocr_accuracy: number;
  ai_accuracy: number;
  confidence_score: number;
  created_at: string;
}

export interface EvaluationItem {
  id: number;
  question_number: string;
  question_text: string;
  max_marks: number;
  student_answer_text: string;
  marks_awarded: number;
  explanation: string;
  missing_concepts: string[];
  missing_keywords: string[];
  confidence_score: number;
  diagram_detected: boolean;
  formula_detected: boolean;
  status: string;
  teacher_override_marks: number | null;
  teacher_notes: string | null;
  evaluated_at: string;
}

interface LiveProgress {
  answer_script_id: number;
  status: string;
  progress: number;
  details: string;
}

interface EvaluationState {
  scripts: AnswerScript[];
  currentScript: AnswerScript | null;
  currentEvaluations: EvaluationItem[];
  liveProgresses: Record<number, LiveProgress>;
  wsConnected: boolean;
  loading: boolean;
  ws: WebSocket | null;
  
  fetchScripts: () => Promise<void>;
  fetchScriptDetails: (id: number) => Promise<void>;
  uploadScripts: (qpId: number, mode: string, files: FileList, customSettings?: any) => Promise<boolean>;
  overrideMarks: (evalId: number, marks: number, notes: string) => Promise<boolean>;
  approveScript: (scriptId: number) => Promise<boolean>;
  connectWebSocket: () => void;
  disconnectWebSocket: () => void;
}

export const useEvaluationStore = create<EvaluationState>((set, get) => ({
  scripts: [],
  currentScript: null,
  currentEvaluations: [],
  liveProgresses: {},
  wsConnected: false,
  loading: false,
  ws: null,
  
  fetchScripts: async () => {
    set({ loading: true });
    try {
      const response = await api.get('/evaluation/answer-scripts');
      set({ scripts: response.data, loading: false });
    } catch (e) {
      console.error(e);
      set({ loading: false });
    }
  },
  
  fetchScriptDetails: async (id) => {
    set({ loading: true });
    try {
      const response = await api.get(`/evaluation/answer-scripts/${id}`);
      set({ 
        currentScript: response.data.script, 
        currentEvaluations: response.data.evaluations,
        loading: false 
      });
    } catch (e) {
      console.error(e);
      set({ loading: false });
    }
  },
  
  uploadScripts: async (qpId, mode, files, customSettings) => {
    try {
      const promises = Array.from(files).map(async (file) => {
        const formData = new FormData();
        formData.append('question_paper_id', String(qpId));
        formData.append('evaluation_mode', mode);
        formData.append('file', file);
        if (customSettings) {
          formData.append('custom_settings', JSON.stringify(customSettings));
        }
        return api.post('/evaluation/upload-answer-script', formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        });
      });
      await Promise.all(promises);
      get().fetchScripts();
      return true;
    } catch (e) {
      console.error(e);
      return false;
    }
  },
  
  overrideMarks: async (evalId, marks, notes) => {
    try {
      await api.post(`/evaluation/evaluations/${evalId}/override`, {
        teacher_override_marks: marks,
        teacher_notes: notes
      });
      
      const current = get().currentScript;
      if (current) {
        get().fetchScriptDetails(current.id);
      }
      return true;
    } catch (e) {
      console.error(e);
      return false;
    }
  },
  
  approveScript: async (scriptId) => {
    try {
      await api.post(`/evaluation/answer-scripts/${scriptId}/approve`);
      const current = get().currentScript;
      if (current && current.id === scriptId) {
        get().fetchScriptDetails(scriptId);
      }
      return true;
    } catch (e) {
      console.error(e);
      return false;
    }
  },
  
  connectWebSocket: () => {
    if (get().wsConnected) return;
    
    const wsUrl = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/ws/evaluations';
    const ws = new WebSocket(wsUrl);
    
    ws.onopen = () => {
      set({ wsConnected: true, ws });
      console.log('WebSocket Session Live');
    };
    
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === 'EVALUATION_PROGRESS') {
          const { answer_script_id, status, progress, details } = data;
          
          set((state) => {
            const nextProgresses = {
              ...state.liveProgresses,
              [answer_script_id]: { answer_script_id, status, progress, details }
            };
            
            const nextScripts = state.scripts.map((s) => {
              if (s.id === answer_script_id) {
                return { ...s, status };
              }
              return s;
            });
            
            let nextCurrentScript = state.currentScript;
            if (nextCurrentScript && nextCurrentScript.id === answer_script_id) {
              nextCurrentScript = { ...nextCurrentScript, status };
              if (status === 'COMPLETED') {
                // Instantly sync database fields for grading detail layouts
                setTimeout(() => get().fetchScriptDetails(answer_script_id), 300);
              }
            }
            
            return {
              liveProgresses: nextProgresses,
              scripts: nextScripts,
              currentScript: nextCurrentScript
            };
          });
        }
      } catch (e) {
        // Safe fail
      }
    };
    
    ws.onclose = () => {
      set({ wsConnected: false, ws: null });
      // Reconnection logic
      setTimeout(() => get().connectWebSocket(), 3500);
    };
  },
  
  disconnectWebSocket: () => {
    const ws = get().ws;
    if (ws) {
      ws.close();
      set({ wsConnected: false, ws: null });
    }
  }
}));

import { useState, useCallback } from 'react';
import type { Quiz, QuizQuestion, QuizGenerateRequest } from '../types';
import * as api from '../api/client';

interface QuizState {
  quiz: Quiz | null;
  currentIndex: number;
  answers: Record<string, string>;
  submitted: boolean;
}

export function useQuiz(kbId: string | null) {
  const [quizzes, setQuizzes] = useState<Quiz[]>([]);
  const [state, setState] = useState<QuizState>({
    quiz: null,
    currentIndex: 0,
    answers: {},
    submitted: false,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchQuizzes = useCallback(async () => {
    if (!kbId) return;

    try {
      setLoading(true);
      const data = await api.getQuizzes(kbId);
      setQuizzes(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to fetch quizzes');
    } finally {
      setLoading(false);
    }
  }, [kbId]);

  const generateQuiz = useCallback(
    async (options: QuizGenerateRequest = {}) => {
      if (!kbId) return null;

      try {
        setLoading(true);
        setError(null);
        const quiz = await api.generateQuiz(kbId, options);
        setQuizzes((prev) => [quiz, ...prev]);
        return quiz;
      } catch (e) {
        setError(e instanceof Error ? e.message : 'Failed to generate quiz');
        return null;
      } finally {
        setLoading(false);
      }
    },
    [kbId]
  );

  const startQuiz = useCallback((quiz: Quiz) => {
    setState({
      quiz,
      currentIndex: 0,
      answers: {},
      submitted: false,
    });
  }, []);

  const answerQuestion = useCallback((questionId: string, answer: string) => {
    setState((prev) => ({
      ...prev,
      answers: { ...prev.answers, [questionId]: answer },
    }));
  }, []);

  const nextQuestion = useCallback(() => {
    setState((prev) => {
      if (!prev.quiz) return prev;
      const maxIndex = prev.quiz.questions.length - 1;
      return {
        ...prev,
        currentIndex: Math.min(prev.currentIndex + 1, maxIndex),
      };
    });
  }, []);

  const prevQuestion = useCallback(() => {
    setState((prev) => ({
      ...prev,
      currentIndex: Math.max(prev.currentIndex - 1, 0),
    }));
  }, []);

  const submitQuiz = useCallback(() => {
    setState((prev) => ({ ...prev, submitted: true }));
  }, []);

  const resetQuiz = useCallback(() => {
    setState({
      quiz: null,
      currentIndex: 0,
      answers: {},
      submitted: false,
    });
  }, []);

  const deleteQuiz = useCallback(
    async (quizId: string) => {
      if (!kbId) return;

      try {
        await api.deleteQuiz(kbId, quizId);
        setQuizzes((prev) => prev.filter((q) => q.id !== quizId));
        if (state.quiz?.id === quizId) {
          resetQuiz();
        }
      } catch (e) {
        setError(e instanceof Error ? e.message : 'Failed to delete quiz');
      }
    },
    [kbId, state.quiz?.id, resetQuiz]
  );

  // Calculate score
  const getScore = useCallback(() => {
    if (!state.quiz || !state.submitted) return null;

    let correct = 0;
    for (const question of state.quiz.questions) {
      if (state.answers[question.id] === question.correct_answer) {
        correct++;
      }
    }

    return {
      correct,
      total: state.quiz.questions.length,
      percentage: Math.round((correct / state.quiz.questions.length) * 100),
    };
  }, [state.quiz, state.answers, state.submitted]);

  const currentQuestion: QuizQuestion | null =
    state.quiz?.questions[state.currentIndex] || null;

  return {
    quizzes,
    quiz: state.quiz,
    currentQuestion,
    currentIndex: state.currentIndex,
    answers: state.answers,
    submitted: state.submitted,
    loading,
    error,
    fetchQuizzes,
    generateQuiz,
    startQuiz,
    answerQuestion,
    nextQuestion,
    prevQuestion,
    submitQuiz,
    resetQuiz,
    deleteQuiz,
    getScore,
  };
}

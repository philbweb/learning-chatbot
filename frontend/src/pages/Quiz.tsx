import { useEffect } from 'react';
import { useQuiz } from '../hooks/useQuiz';
import { QuizView } from '../components/QuizView';

interface QuizPageProps {
  kbId: string;
}

export function Quiz({ kbId }: QuizPageProps) {
  const {
    quizzes,
    quiz,
    currentQuestion,
    currentIndex,
    answers,
    submitted,
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
  } = useQuiz(kbId);

  useEffect(() => {
    fetchQuizzes();
  }, [fetchQuizzes]);

  const handleGenerate = async () => {
    const newQuiz = await generateQuiz({
      num_questions: 5,
      difficulty: 'medium',
      question_types: ['multiple_choice', 'true_false'],
    });
    if (newQuiz) {
      startQuiz(newQuiz);
    }
  };

  // Active quiz view
  if (quiz && currentQuestion) {
    return (
      <div className="h-full overflow-y-auto">
        <QuizView
          quiz={quiz}
          currentQuestion={currentQuestion}
          currentIndex={currentIndex}
          answers={answers}
          submitted={submitted}
          onAnswer={answerQuestion}
          onNext={nextQuestion}
          onPrev={prevQuestion}
          onSubmit={submitQuiz}
          onReset={resetQuiz}
          score={getScore()}
        />
      </div>
    );
  }

  // Quiz selection view
  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-lg font-semibold text-slate-800">Quizzes</h2>
        <button
          onClick={handleGenerate}
          disabled={loading}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
        >
          {loading ? 'Generating...' : 'Generate Quiz'}
        </button>
      </div>

      {error && (
        <div className="mb-4 p-3 bg-red-50 text-red-600 text-sm rounded-lg">
          {error}
        </div>
      )}

      {loading && quizzes.length === 0 ? (
        <div className="text-center text-slate-400 py-12">Loading...</div>
      ) : quizzes.length === 0 ? (
        <div className="text-center text-slate-400 py-12">
          <p className="text-lg mb-2">No quizzes yet</p>
          <p className="text-sm">
            Upload some documents first, then generate a quiz
          </p>
        </div>
      ) : (
        <ul className="space-y-3">
          {quizzes.map((q) => (
            <li
              key={q.id}
              className="bg-white rounded-lg border border-slate-200 p-4 hover:border-slate-300 transition-colors"
            >
              <div className="flex items-center justify-between">
                <div className="flex-1 min-w-0">
                  <h3 className="font-medium text-slate-800 truncate">
                    {q.title}
                  </h3>
                  <p className="text-sm text-slate-500">
                    {q.questions.length} questions •{' '}
                    {new Date(q.created_at).toLocaleDateString()}
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => startQuiz(q)}
                    className="px-4 py-2 bg-blue-50 text-blue-600 rounded-lg hover:bg-blue-100 transition-colors"
                  >
                    Start
                  </button>
                  <button
                    onClick={() => {
                      if (confirm('Delete this quiz?')) {
                        deleteQuiz(q.id);
                      }
                    }}
                    className="p-2 text-slate-400 hover:text-red-500"
                    title="Delete"
                  >
                    <svg
                      className="w-5 h-5"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                      />
                    </svg>
                  </button>
                </div>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

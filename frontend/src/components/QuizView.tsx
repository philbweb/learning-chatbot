import type { Quiz, QuizQuestion } from '../types';

interface QuizViewProps {
  quiz: Quiz;
  currentQuestion: QuizQuestion;
  currentIndex: number;
  answers: Record<string, string>;
  submitted: boolean;
  onAnswer: (questionId: string, answer: string) => void;
  onNext: () => void;
  onPrev: () => void;
  onSubmit: () => void;
  onReset: () => void;
  score: { correct: number; total: number; percentage: number } | null;
}

export function QuizView({
  quiz,
  currentQuestion,
  currentIndex,
  answers,
  submitted,
  onAnswer,
  onNext,
  onPrev,
  onSubmit,
  onReset,
  score,
}: QuizViewProps) {
  const totalQuestions = quiz.questions.length;
  const isLastQuestion = currentIndex === totalQuestions - 1;
  const selectedAnswer = answers[currentQuestion.id];

  if (submitted && score) {
    return (
      <div className="p-6 text-center">
        <h2 className="text-2xl font-bold text-slate-800 mb-4">Quiz Complete!</h2>

        <div className="inline-flex items-center justify-center w-32 h-32 rounded-full bg-gradient-to-br from-blue-500 to-blue-600 text-white mb-6">
          <div>
            <div className="text-3xl font-bold">{score.percentage}%</div>
            <div className="text-sm opacity-80">
              {score.correct}/{score.total}
            </div>
          </div>
        </div>

        <p className="text-slate-600 mb-6">
          {score.percentage >= 80
            ? 'Excellent! You really know this material!'
            : score.percentage >= 60
            ? 'Good job! Keep studying to improve.'
            : 'Keep practicing! Review the material and try again.'}
        </p>

        <div className="space-y-4 max-w-lg mx-auto text-left">
          {quiz.questions.map((q, i) => {
            const userAnswer = answers[q.id];
            const correct = userAnswer === q.correct_answer;

            return (
              <div
                key={q.id}
                className={`p-4 rounded-lg border ${
                  correct
                    ? 'bg-green-50 border-green-200'
                    : 'bg-red-50 border-red-200'
                }`}
              >
                <div className="flex items-start gap-2">
                  <span className={correct ? 'text-green-600' : 'text-red-600'}>
                    {correct ? '✓' : '✗'}
                  </span>
                  <div className="flex-1">
                    <p className="font-medium text-slate-800">
                      {i + 1}. {q.question}
                    </p>
                    {!correct && (
                      <p className="text-sm text-slate-600 mt-1">
                        Your answer: {userAnswer || '(no answer)'}
                        <br />
                        Correct: {q.correct_answer}
                      </p>
                    )}
                    {q.explanation && (
                      <p className="text-sm text-slate-500 mt-2 italic">
                        {q.explanation}
                      </p>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        <button
          onClick={onReset}
          className="mt-8 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          Try Again
        </button>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-2xl mx-auto">
      {/* Progress */}
      <div className="mb-6">
        <div className="flex justify-between text-sm text-slate-600 mb-2">
          <span>
            Question {currentIndex + 1} of {totalQuestions}
          </span>
          <span className="capitalize">{currentQuestion.difficulty}</span>
        </div>
        <div className="w-full bg-slate-200 rounded-full h-2">
          <div
            className="bg-blue-600 h-2 rounded-full transition-all"
            style={{ width: `${((currentIndex + 1) / totalQuestions) * 100}%` }}
          />
        </div>
      </div>

      {/* Question */}
      <div className="bg-white rounded-lg border border-slate-200 p-6 mb-6">
        <h3 className="text-xl font-medium text-slate-800 mb-6">
          {currentQuestion.question}
        </h3>

        {/* Options */}
        <div className="space-y-3">
          {currentQuestion.question_type === 'multiple_choice' &&
            currentQuestion.options?.map((option, i) => (
              <button
                key={i}
                onClick={() => onAnswer(currentQuestion.id, option)}
                className={`w-full text-left p-4 rounded-lg border transition-colors ${
                  selectedAnswer === option
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-slate-200 hover:border-slate-300'
                }`}
              >
                <span className="font-medium text-slate-600 mr-3">
                  {String.fromCharCode(65 + i)}.
                </span>
                {option}
              </button>
            ))}

          {currentQuestion.question_type === 'true_false' && (
            <>
              {['True', 'False'].map((option) => (
                <button
                  key={option}
                  onClick={() => onAnswer(currentQuestion.id, option)}
                  className={`w-full text-left p-4 rounded-lg border transition-colors ${
                    selectedAnswer === option
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-slate-200 hover:border-slate-300'
                  }`}
                >
                  {option}
                </button>
              ))}
            </>
          )}

          {currentQuestion.question_type === 'short_answer' && (
            <input
              type="text"
              value={selectedAnswer || ''}
              onChange={(e) => onAnswer(currentQuestion.id, e.target.value)}
              placeholder="Type your answer..."
              className="w-full p-4 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          )}
        </div>
      </div>

      {/* Navigation */}
      <div className="flex justify-between">
        <button
          onClick={onPrev}
          disabled={currentIndex === 0}
          className="px-4 py-2 text-slate-600 hover:text-slate-800 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          ← Previous
        </button>

        {isLastQuestion ? (
          <button
            onClick={onSubmit}
            disabled={Object.keys(answers).length < totalQuestions}
            className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            Submit Quiz
          </button>
        ) : (
          <button
            onClick={onNext}
            className="px-4 py-2 text-blue-600 hover:text-blue-800"
          >
            Next →
          </button>
        )}
      </div>
    </div>
  );
}

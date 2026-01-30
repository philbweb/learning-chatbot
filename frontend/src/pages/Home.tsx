interface HomeProps {
  onCreateKb: () => void;
}

export function Home({ onCreateKb }: HomeProps) {
  return (
    <div className="h-full flex items-center justify-center bg-gradient-to-br from-slate-50 to-slate-100">
      <div className="text-center max-w-md px-6">
        <div className="w-20 h-20 mx-auto mb-6 rounded-2xl bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center">
          <svg
            className="w-10 h-10 text-white"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"
            />
          </svg>
        </div>

        <h1 className="text-3xl font-bold text-slate-800 mb-4">
          Learning Chatbot
        </h1>

        <p className="text-slate-600 mb-8">
          Create knowledge bases from your documents, ask questions, and test
          your understanding with auto-generated quizzes.
        </p>

        <button
          onClick={onCreateKb}
          className="px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors shadow-lg shadow-blue-200"
        >
          Create Your First Knowledge Base
        </button>

        <div className="mt-12 grid grid-cols-3 gap-6 text-center">
          <div>
            <div className="text-2xl mb-2">📚</div>
            <p className="text-sm text-slate-600">Upload Documents</p>
          </div>
          <div>
            <div className="text-2xl mb-2">💬</div>
            <p className="text-sm text-slate-600">Ask Questions</p>
          </div>
          <div>
            <div className="text-2xl mb-2">📝</div>
            <p className="text-sm text-slate-600">Take Quizzes</p>
          </div>
        </div>
      </div>
    </div>
  );
}

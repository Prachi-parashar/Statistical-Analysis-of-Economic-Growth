import React from 'react'
import { AlertTriangle, RefreshCw } from 'lucide-react'

export default class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props)
    this.state = { hasError: false, error: null }
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error }
  }

  componentDidCatch(error, errorInfo) {
    console.error('ErrorBoundary caught error:', error, errorInfo)
  }

  handleRetry = () => {
    this.setState({ hasError: false, error: null })
    if (this.props.onRetry) {
      this.props.onRetry()
    }
  }

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback
      }
      return (
        <div className="rounded-xl border border-red-200 dark:border-red-900/60 bg-red-50/60 dark:bg-red-950/20 p-5 text-center my-2">
          <div className="w-10 h-10 rounded-full bg-red-100 dark:bg-red-900/40 text-red-600 dark:text-red-400 flex items-center justify-center mx-auto mb-2.5">
            <AlertTriangle size={18} />
          </div>
          <h4 className="text-sm font-semibold text-red-900 dark:text-red-200">
            {this.props.title || 'Component Display Error'}
          </h4>
          <p className="text-xs text-red-700 dark:text-red-300/80 mt-1 max-w-md mx-auto">
            {this.state.error?.message || 'A runtime error occurred while displaying this section.'}
          </p>
          <button
            onClick={this.handleRetry}
            className="mt-3 inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg bg-red-600 hover:bg-red-700 text-white transition-colors shadow-sm"
          >
            <RefreshCw size={12} />
            Retry View
          </button>
        </div>
      )
    }

    return this.props.children
  }
}

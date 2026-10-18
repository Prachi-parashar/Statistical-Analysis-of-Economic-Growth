import { useState, useEffect } from 'react'
import { Database, Sun, Moon } from 'lucide-react'
import { getProjectInfo } from '../api/projectApi'
import { useTheme } from '../context/ThemeContext.jsx'

export default function Header() {
  const [meta, setMeta] = useState(null)
  const { theme, toggleTheme } = useTheme()

  useEffect(() => {
    getProjectInfo().then(res => {
      if (res) setMeta(res)
    }).catch(() => {})
  }, [])

  const periodStr = meta?.min_year && meta?.max_year
    ? `${meta.min_year}–${meta.max_year}`
    : (meta?.start_year && meta?.end_year ? `${meta.start_year}–${meta.end_year}` : '')

  return (
    <header className="bg-white dark:bg-slate-800 border-b border-slate-200 dark:border-slate-700/80 px-4 sm:px-6 py-3.5
                       flex items-center gap-4 flex-shrink-0 min-h-[60px] transition-colors duration-150">

      {/* Desktop title */}
      <div className="hidden lg:flex items-center gap-3 min-w-0">
        <div className="w-8 h-8 rounded-lg overflow-hidden flex items-center justify-center flex-shrink-0 bg-white border border-slate-200 dark:border-slate-700 shadow-sm p-0.5">
          <img
            src="/arthalens-mark.png"
            alt="ArthaLens Logo"
            className="w-full h-full object-contain"
          />
        </div>
        <div className="min-w-0">
          <h1 className="text-sm font-semibold text-slate-800 dark:text-slate-100 leading-tight truncate">
            Statistical Analysis of Economic Growth and Its Determinants in India
          </h1>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
            Statistical Analysis &amp; Economic Data Dashboard
          </p>
        </div>
      </div>

      {/* Mobile title — padded for hamburger */}
      <div className="lg:hidden pl-9 min-w-0 flex items-center gap-2">
        <div className="w-7 h-7 rounded-md overflow-hidden flex items-center justify-center flex-shrink-0 bg-white border border-slate-200 dark:border-slate-700 p-0.5">
          <img
            src="/arthalens-mark.png"
            alt="ArthaLens Logo"
            className="w-full h-full object-contain"
          />
        </div>
        <div className="min-w-0">
          <div className="flex items-center text-xs font-extrabold tracking-tight leading-tight">
            <span className="text-[#091e33] dark:text-slate-100">Artha</span>
            <span className="text-[#1a7c55] dark:text-emerald-400">Lens</span>
          </div>
          <p className="text-[10px] text-slate-500 dark:text-slate-400 truncate">India Economic Growth Study</p>
        </div>
      </div>

      {/* Right-side theme toggle & meta chip */}
      <div className="ml-auto flex items-center gap-2.5 flex-shrink-0">
        {/* Theme Toggle Button */}
        <button
          onClick={toggleTheme}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium border
                     bg-slate-50 hover:bg-slate-100 text-slate-700 border-slate-200
                     dark:bg-slate-700/70 dark:hover:bg-slate-700 dark:text-slate-200 dark:border-slate-600
                     transition-colors shadow-sm select-none cursor-pointer"
          title={`Switch to ${theme === 'light' ? 'Dark' : 'Light'} Mode`}
          aria-label={`Switch to ${theme === 'light' ? 'Dark' : 'Light'} Mode`}
        >
          {theme === 'light' ? (
            <>
              <Moon size={14} className="text-slate-600 dark:text-slate-300 flex-shrink-0" />
              <span className="hidden xs:inline">Dark Mode</span>
            </>
          ) : (
            <>
              <Sun size={14} className="text-amber-400 flex-shrink-0" />
              <span className="hidden xs:inline">Light Mode</span>
            </>
          )}
        </button>

        <span className="hidden sm:inline-flex items-center gap-1.5 px-2.5 py-1
                         bg-primary-50 text-primary-700 dark:bg-primary-950/60 dark:text-primary-300
                         rounded-full text-xs font-medium border border-primary-100 dark:border-primary-800/80 whitespace-nowrap">
          <Database size={11} aria-hidden="true" />
          World Bank WDI · India{periodStr ? ` · ${periodStr}` : ''}
        </span>
        {/* Mobile chip (shorter) */}
        <span className="sm:hidden inline-flex items-center gap-1 px-2 py-1
                         bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 rounded-full text-xs font-medium">
          WDI{periodStr ? ` · ${periodStr}` : ''}
        </span>
      </div>
    </header>
  )
}

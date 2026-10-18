import { useState, useEffect } from 'react'
import { NavLink } from 'react-router-dom'
import {
  LayoutDashboard, Database, BarChart2, Activity,
  GitBranch, TrendingUp, Stethoscope, FileText,
  Info, ChevronLeft, ChevronRight, Menu, X
} from 'lucide-react'
import { getProjectInfo } from '../api/projectApi'

const NAV_ITEMS = [
  { to: '/',                       label: 'Dashboard',               icon: LayoutDashboard },
  { to: '/dataset',                label: 'Dataset',                 icon: Database        },
  { to: '/descriptive-statistics', label: 'Descriptive Statistics',  icon: BarChart2       },
  { to: '/probability',            label: 'Probability Distribution',icon: Activity        },
  { to: '/correlation',            label: 'Correlation',             icon: GitBranch       },
  { to: '/regression',             label: 'Regression',              icon: TrendingUp      },
  { to: '/diagnostics',            label: 'Diagnostics',             icon: Stethoscope     },
  { to: '/reports',                label: 'Reports',                 icon: FileText        },
  { to: '/about',                  label: 'About',                   icon: Info            },
]

function NavItems({ collapsed, onNavigate }) {
  const linkClass = ({ isActive }) =>
    [
      'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium',
      'transition-colors duration-150 focus-visible:outline-none',
      'focus-visible:ring-2 focus-visible:ring-primary-400',
      isActive
        ? 'bg-primary-600 text-white shadow-sm'
        : 'text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700/70 hover:text-slate-900 dark:hover:text-white',
    ].join(' ')

  return (
    <nav className="flex-1 px-2 py-3 space-y-0.5 overflow-y-auto" aria-label="Main navigation">
      {NAV_ITEMS.map(({ to, label, icon: Icon }) => (
        <NavLink
          key={to}
          to={to}
          end={to === '/'}
          className={linkClass}
          onClick={onNavigate}
          title={collapsed ? label : undefined}
          aria-label={label}
        >
          <Icon size={17} className="flex-shrink-0" aria-hidden="true" />
          {!collapsed && <span className="truncate">{label}</span>}
        </NavLink>
      ))}
    </nav>
  )
}

function SidebarLogo({ collapsed }) {
  return (
    <div className="flex items-center gap-3 px-3 py-3.5 border-b border-slate-200 dark:border-slate-700/80 flex-shrink-0">
      <div className="w-9 h-9 bg-white dark:bg-slate-800 rounded-lg flex items-center justify-center flex-shrink-0 shadow-sm border border-slate-200 dark:border-slate-700 p-0.5 overflow-hidden">
        <img
          src="/arthalens-mark.png"
          alt="ArthaLens Logo"
          className="w-full h-full object-contain"
        />
      </div>
      {!collapsed && (
        <div className="min-w-0">
          <div className="flex items-center text-[15px] font-extrabold tracking-tight leading-tight mb-0.5">
            <span className="text-[#091e33] dark:text-slate-100">Artha</span>
            <span className="text-[#1a7c55] dark:text-emerald-400">Lens</span>
          </div>
          <p className="text-xs font-semibold text-slate-800 dark:text-slate-100 leading-tight">India Economic</p>
          <p className="text-[11px] text-slate-500 dark:text-slate-400 leading-tight">Growth Study</p>
        </div>
      )}
    </div>
  )
}

function SidebarFooter({ collapsed }) {
  const [meta, setMeta] = useState(null)

  useEffect(() => {
    getProjectInfo().then(res => {
      if (res) setMeta(res)
    }).catch(() => {})
  }, [])

  if (collapsed) return null

  const periodStr = meta?.min_year && meta?.max_year
    ? `${meta.min_year}–${meta.max_year}`
    : (meta?.start_year && meta?.end_year ? `${meta.start_year}–${meta.end_year}` : '')

  const obsStr = meta?.observation_count ? `n=${meta.observation_count}` : ''

  return (
    <div className="px-3 py-3 border-t border-slate-100 dark:border-slate-700/70 flex-shrink-0">
      <div className="px-2 py-2 bg-slate-50 dark:bg-slate-900/50 rounded-lg border border-slate-100 dark:border-slate-800">
        <p className="text-xs font-medium text-slate-500 dark:text-slate-400">Data Source</p>
        <p className="text-xs text-slate-400 dark:text-slate-500 mt-0.5">World Bank WDI</p>
        <p className="text-xs text-slate-400 dark:text-slate-500">
          India{periodStr ? ` · ${periodStr}` : ''}{obsStr ? ` · ${obsStr}` : ''}
        </p>
      </div>
    </div>
  )
}

export default function Sidebar() {
  const [collapsed, setCollapsed] = useState(false)
  const [mobileOpen, setMobileOpen] = useState(false)

  const closeMobile = () => setMobileOpen(false)

  return (
    <>
      {/* ── Mobile hamburger ── */}
      <button
        className="lg:hidden fixed top-3 left-3 z-50 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700
                   text-slate-700 dark:text-slate-200 rounded-lg p-2 shadow-sm hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors"
        onClick={() => setMobileOpen((v) => !v)}
        aria-label={mobileOpen ? 'Close navigation' : 'Open navigation'}
        aria-expanded={mobileOpen}
      >
        {mobileOpen ? <X size={18} /> : <Menu size={18} />}
      </button>

      {/* ── Mobile backdrop ── */}
      {mobileOpen && (
        <div
          className="lg:hidden fixed inset-0 bg-black/40 z-40 backdrop-blur-sm"
          onClick={closeMobile}
          aria-hidden="true"
        />
      )}

      {/* ── Mobile sidebar ── */}
      <aside
        className={[
          'lg:hidden fixed top-0 left-0 h-full w-64 bg-white dark:bg-slate-800 border-r border-slate-200 dark:border-slate-700',
          'flex flex-col z-50 shadow-2xl transition-transform duration-200 ease-in-out',
          mobileOpen ? 'translate-x-0' : '-translate-x-full',
        ].join(' ')}
        aria-hidden={!mobileOpen}
      >
        <SidebarLogo collapsed={false} />
        <NavItems collapsed={false} onNavigate={closeMobile} />
        <SidebarFooter collapsed={false} />
      </aside>

      {/* ── Desktop sidebar ── */}
      <aside
        className={[
          'hidden lg:flex flex-col bg-white dark:bg-slate-800 border-r border-slate-200 dark:border-slate-700/80',
          'transition-all duration-200 ease-in-out flex-shrink-0 h-full',
          collapsed ? 'w-16' : 'w-60',
        ].join(' ')}
      >
        <SidebarLogo collapsed={collapsed} />
        <NavItems collapsed={collapsed} onNavigate={() => {}} />
        <SidebarFooter collapsed={collapsed} />

        {/* Collapse toggle */}
        <button
          onClick={() => setCollapsed((v) => !v)}
          className="flex items-center justify-center py-3 border-t border-slate-200 dark:border-slate-700/80
                     text-slate-400 dark:text-slate-500 hover:text-slate-700 dark:hover:text-slate-200 hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors
                     flex-shrink-0"
          aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          {collapsed
            ? <ChevronRight size={15} aria-hidden="true" />
            : <ChevronLeft  size={15} aria-hidden="true" />
          }
        </button>
      </aside>
    </>
  )
}

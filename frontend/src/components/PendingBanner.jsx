import { AlertTriangle, Info } from 'lucide-react'

/**
 * Reusable banner shown wherever backend data is pending.
 * variant: 'amber' (default) | 'blue'
 */
export default function PendingBanner({
  message = 'Values will be loaded from the backend API.',
  variant = 'amber',
}) {
  const styles = {
    amber: {
      wrap: 'bg-amber-50 border-amber-200 text-amber-700',
      Icon: AlertTriangle,
    },
    blue: {
      wrap: 'bg-blue-50 border-blue-200 text-blue-700',
      Icon: Info,
    },
  }
  const { wrap, Icon } = styles[variant] || styles.amber

  return (
    <div className={`flex items-start gap-2 p-3 border rounded-xl text-xs leading-relaxed ${wrap}`}>
      <Icon size={13} className="mt-0.5 flex-shrink-0" aria-hidden="true" />
      <span>{message}</span>
    </div>
  )
}

import React from 'react'
import { Spinner, SpinnerSize, ISpinnerStyles } from '@fluentui/react'
import styles from './LoadingSpinner.module.css'

interface LoadingSpinnerProps {
  label?: string
  size?: SpinnerSize
  customSize?: number
  fullscreen?: boolean
  centered?: boolean
  overlay?: boolean
  overlayOpacity?: number
}

const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  label = 'Loading...',
  size = SpinnerSize.large,
  customSize = 48, // Default custom size in pixels
  fullscreen = false,
  centered = false,
  overlay = false,
  overlayOpacity = 0.8
}) => {
  // Custom spinner styles to make it larger
  const spinnerStyles: ISpinnerStyles = {
    circle: {
      width: customSize,
      height: customSize,
      borderWidth: Math.max(3, customSize / 16) // Scale border width with size
    },
    label: {
      fontSize: '16px',
      marginTop: '12px'
    }
  }

  // Determine which CSS classes to apply
  const wrapperClassNames = [styles.spinnerWrapper]

  if (fullscreen) {
    wrapperClassNames.push(styles.spinnerFullscreen)
  }

  if (centered) {
    wrapperClassNames.push(styles.spinnerCenter)
  }

  if (overlay) {
    wrapperClassNames.push(styles.spinnerOverlay)
    // Apply custom opacity via inline style
    const overlayStyle = {
      backgroundColor: `rgba(255, 255, 255, ${overlayOpacity})`
    }

    return (
      <div className={wrapperClassNames.join(' ')} style={overlayStyle}>
        <Spinner size={size} label={label} styles={spinnerStyles} />
      </div>
    )
  }

  return (
    <div className={wrapperClassNames.join(' ')}>
      <Spinner size={size} label={label} styles={spinnerStyles} />
    </div>
  )
}

export default LoadingSpinner

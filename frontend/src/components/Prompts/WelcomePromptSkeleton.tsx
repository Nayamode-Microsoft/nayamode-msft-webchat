import React from 'react'
import { Stack, Shimmer, ShimmerElementType } from '@fluentui/react'
import styles from './prompt.module.css'

export const WelcomePromptSkeleton: React.FC = () => {
  // Shimmer element styles
  const logoShimmerStyles = { root: { width: 62, height: 62, margin: '0 auto' } }
  const titleShimmerStyles = { root: { width: '60%', height: 28, margin: '36px auto 0' } }
  const subtitleShimmerStyles = { root: { width: '80%', height: 20, margin: '20px auto 0' } }
  const headingShimmerStyles = { root: { width: '40%', height: 24, marginBottom: '16px' } }
  const buttonShimmerStyles = { root: { width: '100%', height: 44, marginBottom: '8px' } }
  const footerShimmerStyles = { root: { width: '70%', height: 16, margin: '8px auto' } }

  return (
    <Stack className={styles.chatEmptyState}>
      {/* Logo placeholder */}
      <Shimmer
        shimmerElements={[{ type: ShimmerElementType.circle, width: 62, height: 62 }]}
        styles={logoShimmerStyles}
      />

      <Stack className={styles.welcomeContainer}>
        <Stack className={styles.headerSection}>
          {/* Title placeholder */}
          <Shimmer
            shimmerElements={[{ type: ShimmerElementType.line, width: '100%', height: 28 }]}
            styles={titleShimmerStyles}
          />

          {/* Subtitle placeholder */}
          <Shimmer
            shimmerElements={[{ type: ShimmerElementType.line, width: '100%', height: 20 }]}
            styles={subtitleShimmerStyles}
          />
        </Stack>

        <Stack className={styles.promptsSection} styles={{ root: { width: '100%' } }}>
          {/* Section heading placeholder */}
          <Shimmer
            shimmerElements={[{ type: ShimmerElementType.line, width: '100%', height: 24 }]}
            styles={headingShimmerStyles}
          />

          <Stack tokens={{ childrenGap: 8 }} styles={{ root: { width: '100%' } }}>
            {/* Button placeholders - 4 of them */}
            {[...Array(4)].map((_, index) => (
              <Shimmer
                key={index}
                shimmerElements={[{ type: ShimmerElementType.line, width: '100%', height: 44 }]}
                styles={buttonShimmerStyles}
              />
            ))}
          </Stack>
        </Stack>

        <Stack className={styles.footerSection}>
          {/* Footer text placeholders */}
          <Shimmer
            shimmerElements={[{ type: ShimmerElementType.line, width: '100%', height: 16 }]}
            styles={footerShimmerStyles}
          />
          <Shimmer
            shimmerElements={[{ type: ShimmerElementType.line, width: '80%', height: 16 }]}
            styles={footerShimmerStyles}
          />
        </Stack>
      </Stack>
    </Stack>
  )
}

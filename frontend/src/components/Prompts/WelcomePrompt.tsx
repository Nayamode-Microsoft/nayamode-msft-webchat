import React from 'react'
import { Stack, Text, DefaultButton, FontWeights } from '@fluentui/react'

import styles from './prompt.module.css'
import { WelcomePromptSkeleton } from './WelcomePromptSkeleton'

interface WelcomeGreetingProps {
  logo?: string
  loading: boolean
  showSuggestedPrompts?: boolean
  onPromptSelect?: (prompt: string) => void
}

export const WelcomePrompt: React.FC<WelcomeGreetingProps> = ({
  logo,
  loading,
  showSuggestedPrompts = false,
  onPromptSelect
}) => {
  const suggestedPrompts = [
    'Partner Practice Lead',
    'Partner Solution Architect',
    'Partner Seller',
    'Partner Adoption and Change Management'
  ]

  const handlePromptClick = (prompt: string): void => {
    if (onPromptSelect) {
      onPromptSelect(prompt)
    }
  }

  if (loading) {
    return <WelcomePromptSkeleton />
  }

  return (
    <Stack className={styles.chatEmptyState}>
      <img src={logo} className={styles.chatIcon} aria-hidden="true" />

      <Stack className={styles.welcomeContainer}>
        <Stack className={styles.headerSection}>
          <Text variant="xxLarge" className={styles.welcomeTitle}>
            Welcome to Nayamode AI Assistant
          </Text>
          <Text variant="large" className={styles.welcomeSubtitle}>
            Your intelligent partner for business productivity and insights
          </Text>
        </Stack>

        {showSuggestedPrompts && (
          <>
            <Stack className={styles.promptsSection}>
              <Text variant="large" styles={{ root: { fontWeight: FontWeights.semibold, marginBottom: '16px' } }}>
                What role best describes you?
              </Text>

              <Stack tokens={{ childrenGap: 8 }}>
                {suggestedPrompts.map((prompt, index) => (
                  <DefaultButton
                    key={index}
                    className={styles.promptButton}
                    onClick={() => handlePromptClick(prompt)}
                    text={prompt}
                    iconProps={{ iconName: 'ChevronRight', className: styles.buttonIcon }}
                  />
                ))}
              </Stack>
            </Stack>

            <Stack className={styles.footerSection}>
              <Text className={styles.footerText}>
                You can ask me questions, request analysis, or get help with various tasks.
              </Text>
              <Text className={styles.footerText}>I'm here to assist you with your business needs!</Text>
            </Stack>
          </>
        )}
      </Stack>
    </Stack>
  )
}

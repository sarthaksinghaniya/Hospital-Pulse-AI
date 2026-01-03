import React from 'react'
import { Card, CardContent, Typography, Stack } from '@mui/material'

export default function SectionCard({ title, subtitle, action, children }) {
  return (
    <Card
      elevation={1}
      sx={{
        borderRadius: 2,
        height: '100%',
        bgcolor: '#fdfefe',
        border: '1px solid #e6ecf2',
        transition: 'box-shadow 180ms ease, transform 180ms ease',
        '&:hover': { boxShadow: 4, transform: 'translateY(-2px)' },
      }}
    >
      <CardContent>
        <Stack direction="row" justifyContent="space-between" alignItems="center" mb={1.5} spacing={1}>
          <div>
            <Typography variant="h6" fontWeight={700} gutterBottom>
              {title}
            </Typography>
            {subtitle && (
              <Typography variant="body2" color="text.secondary">
                {subtitle}
              </Typography>
            )}
          </div>
          {action && <div>{action}</div>}
        </Stack>
        {children}
      </CardContent>
    </Card>
  )
}

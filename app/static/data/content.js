// Shared content data for reusable page components.
window.GA_PORTAL_CONTENT = {
  templates: [
    {
      id: 'hearing-reminder',
      title: 'Hearing Reminder',
      type: 'Hearing',
      body: `Subject: Student Conduct Hearing Reminder\n\nHello [Student Name],\n\nThis is a reminder that your Student Conduct hearing is scheduled for [Date] at [Time] in [Location/Zoom Link]. Please review your notice and bring any relevant materials.\n\nIf you have a scheduling conflict, respond within one business day.\n\nOffice of Student Conduct`
    },
    {
      id: 'missed-hearing',
      title: 'Missed Hearing Notice',
      type: 'Hearing',
      body: `Subject: Missed Hearing Follow-Up\n\nHello [Student Name],\n\nOur records show you did not attend your scheduled hearing on [Date]. Please reply by [Deadline] to coordinate next steps.\n\nFailure to respond may result in a decision based on available information.\n\nOffice of Student Conduct`
    },
    {
      id: 'sanction-follow-up',
      title: 'Sanction Completion Follow-Up',
      type: 'Sanctions',
      body: `Subject: Sanction Completion Status\n\nHello [Student Name],\n\nThis is a reminder that your assigned sanction ([Sanction Name]) is due on [Due Date]. Please submit completion documentation through [Submission Method].\n\nContact us if you need clarification.\n\nOffice of Student Conduct`
    },
    {
      id: 'hold-message',
      title: 'Hold-Related Message',
      type: 'Holds',
      body: `Subject: Conduct Hold Status\n\nHello [Student Name],\n\nA conduct hold is currently active because required sanctions are still pending. The hold can be reviewed once completion is verified in Maxient and any required tracking sheet updates are complete.\n\nOffice of Student Conduct`
    },
    {
      id: 'parent-letter',
      title: 'Parent Letter Coordination',
      type: 'Parent Letters',
      body: `Subject: Parent Letter Processing Update\n\nHi [Supervisor/Staff Name],\n\nThe parent letter request for [Student Name/Case ID] is prepared and pending final review. Address verification has been completed against SIS records.\n\nPlease confirm approval to send.\n\nThank you,\n[GA Name]`
    },
    {
      id: 'staff-follow-up',
      title: 'Staff Follow-Up',
      type: 'Staff',
      body: `Subject: Case Follow-Up Summary\n\nHi [Staff Name],\n\nQuick status update for case [Case ID]:\n- Hearing date: [Date]\n- Outcome entered: [Yes/No]\n- Sanction tracking updated: [Yes/No]\n- Open items: [List]\n\nPlease let me know if additional review is needed.\n\n[GA Name]`
    }
  ]
};

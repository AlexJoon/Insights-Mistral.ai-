/**
 * Markdown parser utility
 * Converts markdown text to semantic HTML
 */

export function parseMarkdownToHTML(markdown: string): string {
  let html = markdown;

  // Code blocks (do this first to protect code content)
  html = html.replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>');

  // Inline code
  html = html.replace(/`([^`]+)`/g, '<code>$1</code>');

  // Headers
  html = html.replace(/^### (.*$)/gim, '<h3>$1</h3>');
  html = html.replace(/^## (.*$)/gim, '<h2>$1</h2>');
  html = html.replace(/^# (.*$)/gim, '<h1>$1</h1>');

  // Bold
  html = html.replace(/\*\*\*(.+?)\*\*\*/g, '<strong><em>$1</em></strong>');
  html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');

  // Italic
  html = html.replace(/\*(.+?)\*/g, '<em>$1</em>');
  html = html.replace(/_(.+?)_/g, '<em>$1</em>');

  // Links
  html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>');

  // Lists - detect list items
  html = html.replace(/^[\*\-] (.+)$/gim, '<li>$1</li>');
  html = html.replace(/^\d+\. (.+)$/gim, '<li>$1</li>');

  // Wrap consecutive list items in ul
  html = html.replace(/(<li>.*?<\/li>\n?)+/g, (match) => {
    return `<ul>${match.replace(/\n/g, '')}</ul>\n`;
  });

  // Split into paragraphs by double newlines
  const paragraphs = html.split(/\n\n+/);

  html = paragraphs.map(para => {
    para = para.trim();

    // Don't wrap if already a block element
    if (para.startsWith('<h') ||
        para.startsWith('<ul') ||
        para.startsWith('<ol') ||
        para.startsWith('<pre') ||
        para.startsWith('<blockquote')) {
      return para;
    }

    // Replace single newlines within paragraphs with <br>
    para = para.replace(/\n/g, '<br>');

    // Wrap in paragraph tag
    return `<p>${para}</p>`;
  }).join('\n');

  return html;
}

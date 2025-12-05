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

  // Horizontal rules
  html = html.replace(/^(?:---+|___+|\*\*\*+)$/gim, '<hr>');

  // Headers (order matters - h6 to h1)
  html = html.replace(/^###### (.*$)/gim, '<h6>$1</h6>');
  html = html.replace(/^##### (.*$)/gim, '<h5>$1</h5>');
  html = html.replace(/^#### (.*$)/gim, '<h4>$1</h4>');
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

  // Process lists with proper nesting support
  const lines = html.split('\n');
  const processedLines: string[] = [];
  let i = 0;

  while (i < lines.length) {
    const line = lines[i];

    // Check if this is a list item (unordered or ordered)
    const unorderedMatch = line.match(/^([\*\-])\s+(.+)$/);
    const orderedMatch = line.match(/^(\d+\.)\s+(.+)$/);

    if (unorderedMatch || orderedMatch) {
      // Start of a top-level list
      const listItems: string[] = [];
      const isOrdered = !!orderedMatch;

      // Collect all consecutive list items (including nested ones)
      while (i < lines.length) {
        const currentLine = lines[i];
        const topMatch = currentLine.match(/^[\*\-]\s+(.+)$/);
        const topOrderedMatch = currentLine.match(/^\d+\.\s+(.+)$/);
        const nestedMatch = currentLine.match(/^\s+([\*\-])\s+(.+)$/);

        if (topMatch || topOrderedMatch) {
          // Top-level list item
          const content = topMatch ? topMatch[1] : topOrderedMatch![1];
          listItems.push(`<li>${content}</li>`);
          i++;
        } else if (nestedMatch) {
          // Nested list item - add as nested ul within previous li
          const nestedItems: string[] = [];

          while (i < lines.length) {
            const nestedLine = lines[i];
            const nestedItemMatch = nestedLine.match(/^\s+([\*\-])\s+(.+)$/);

            if (nestedItemMatch) {
              nestedItems.push(`<li>${nestedItemMatch[2]}</li>`);
              i++;
            } else {
              break;
            }
          }

          // Insert nested ul into the last list item
          if (listItems.length > 0 && nestedItems.length > 0) {
            const lastIndex = listItems.length - 1;
            listItems[lastIndex] = listItems[lastIndex].replace('</li>', `<ul>${nestedItems.join('')}</ul></li>`);
          }
        } else {
          break;
        }
      }

      // Wrap in ul or ol
      const tag = isOrdered ? 'ol' : 'ul';
      processedLines.push(`<${tag}>${listItems.join('')}</${tag}>`);
    } else {
      // Not a list item, keep as is
      processedLines.push(line);
      i++;
    }
  }

  html = processedLines.join('\n');

  // Split into paragraphs by double newlines
  const paragraphs = html.split(/\n\n+/);

  html = paragraphs.map(para => {
    para = para.trim();

    // Don't wrap if already a block element or horizontal rule
    if (para.startsWith('<h') ||
        para.startsWith('<ul') ||
        para.startsWith('<ol') ||
        para.startsWith('<pre') ||
        para.startsWith('<hr') ||
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

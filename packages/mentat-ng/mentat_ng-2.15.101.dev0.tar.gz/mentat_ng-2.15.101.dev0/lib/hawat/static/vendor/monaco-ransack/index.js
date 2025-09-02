function registerRansack(monaco) {
  monaco.languages.register({ id: 'ransack' });

  monaco.languages.setMonarchTokensProvider('ransack', {
    defaultToken: 'invalid',
    ignoreCase: true,
    tokenizer: {
      root: [
        // Keywords
        [/\b(and|or|not|in|contains)\b/, 'keyword'],

        // Operators
        [/==|>=|<=|=|>|<|\+|-|\*|\/|%|\|\||&&|!|\?\?|\./, 'operator'],

        // Constants
        [/\b\d{1,3}(?:\.\d{1,3}){3}\b/, 'number.ipv4'],
        [/\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}-\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/, 'number.ipv4_range'],
        [/\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\/\d{1,2}/, 'number.ipv4_cidr'],
        [/[:a-fA-F0-9]+:[:a-fA-F0-9]*/, 'number.ipv6'],
        [/([0-9]+[D|d])?[0-9]{2}:[0-9]{2}:[0-9]{2}/, 'number.timedelta'],
        [/[0-9]{4}-[0-9]{2}-[0-9]{2}([T|t]?[0-9]{2}:[0-9]{2}:[0-9]{2}(?:\.[0-9]+)?(?:[Zz]|(?:[+-][0-9]{2}:[0-9]{2}))?)?/, 'number.datetime'],
        [/\d+(\.\d+)?([eE][+-]?\d+)?/, 'number'],

        // Strings
        [/".*?"/, 'string'],
        [/'.*?'/, 'string'],

        // Variables
        [/\.?[_a-zA-Z][-_a-zA-Z0-9]*(\.[_a-zA-Z][-_a-zA-Z0-9]*)*/, 'variable'],

        // Brackets
        [/[()\[\]]/, '@brackets'],

        // Delimiters
        [/\,/, 'delimiter'],

        // Ignore whitespace
        [/\s+/, 'white']
      ]
    }
  });

  monaco.languages.setLanguageConfiguration('ransack', {
    autoClosingPairs: [
      { open: '"', close: '"' },
      { open: "'", close: "'" },
      { open: '(', close: ')' },
      { open: '[', close: ']' },
    ],
    brackets: [
      ['(', ')'],
      ['[', ']'],
    ],
    surroundingPairs: [
      { open: '"', close: '"' },
      { open: "'", close: "'" },
    ],
  });

  monaco.languages.registerCompletionItemProvider('ransack', {
    provideCompletionItems: () => {
      const suggestions = [
        'and', 'or', 'not', 'in', 'contains',
      ].map(word => ({
        label: word,
        kind: monaco.languages.CompletionItemKind.Operator,
        insertText: word
      }));

      return { suggestions };
    }
  });
}

window.registerRansack = registerRansack;


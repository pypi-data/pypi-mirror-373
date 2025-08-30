/**
 * Interface for ticker data
 */
interface TickerData {
  name: string;
  type: string;
  sector: string;
  industry: string;
  source: string;
}

/**
 * Interface for search result
 */
interface SearchResult {
  ticker: string;
  name: string;
  type: string;
  source: string;
  score: number;
}

/**
 * Tools for interacting with web services and external APIs
 */
export class WebTools {
  private tickers: Record<string, TickerData> | null = null;

  constructor() {
    // Tickers will be loaded lazily on first use
  }

  /**
   * Load tickers data lazily and cache it
   * @returns Promise that resolves to the tickers data
   */
  private async loadTickers(): Promise<Record<string, TickerData>> {
    if (this.tickers === null) {
      try {
        // Dynamic import to load the JSON file only when needed
        const tickersModule = await import('./tickers.json');
        this.tickers = tickersModule.default as Record<string, TickerData>;
      } catch (error) {
        console.error('Failed to load tickers data:', error);
        this.tickers = {}; // Fallback to empty object
      }
    }
    return this.tickers;
  }

  /**
   * Calculate Levenshtein distance between two strings
   * @param str1 First string
   * @param str2 Second string
   * @returns Levenshtein distance
   */
  private levenshteinDistance(str1: string, str2: string): number {
    const matrix = [];
    const len1 = str1.length;
    const len2 = str2.length;

    if (len1 === 0) return len2;
    if (len2 === 0) return len1;

    // Create matrix
    for (let i = 0; i <= len2; i++) {
      matrix[i] = [i];
    }

    for (let j = 0; j <= len1; j++) {
      matrix[0][j] = j;
    }

    // Fill matrix
    for (let i = 1; i <= len2; i++) {
      for (let j = 1; j <= len1; j++) {
        if (str2.charAt(i - 1) === str1.charAt(j - 1)) {
          matrix[i][j] = matrix[i - 1][j - 1];
        } else {
          matrix[i][j] = Math.min(
            matrix[i - 1][j - 1] + 1, // substitution
            matrix[i][j - 1] + 1, // insertion
            matrix[i - 1][j] + 1 // deletion
          );
        }
      }
    }

    return matrix[len2][len1];
  }

  /**
   * Calculate fuzzy match score between query and target string
   * @param query Search query
   * @param target Target string to match against
   * @returns Score between 0 and 100 (higher is better)
   */
  private fuzzyMatchScore(query: string, target: string): number {
    const queryLower = query.toLowerCase().trim();
    const targetLower = target.toLowerCase().trim();

    // Exact match gets perfect score
    if (queryLower === targetLower) {
      return 100;
    }

    // Substring matches get high scores
    if (targetLower.includes(queryLower)) {
      const ratio = queryLower.length / targetLower.length;
      return Math.max(70, 90 * ratio);
    }

    // Prefix matches get good scores
    if (targetLower.startsWith(queryLower)) {
      const ratio = queryLower.length / targetLower.length;
      return Math.max(60, 80 * ratio);
    }

    // Calculate Levenshtein distance for fuzzy matching
    const distance = this.levenshteinDistance(queryLower, targetLower);
    const maxLength = Math.max(queryLower.length, targetLower.length);

    if (maxLength === 0) return 0;

    // Convert distance to similarity score (0-100)
    const similarity = (1 - distance / maxLength) * 100;

    // Only return matches with reasonable similarity
    return similarity > 50 ? similarity : 0;
  }

  /**
   * Search words in a string for fuzzy matches
   * @param query Search query
   * @param text Text to search in
   * @returns Best match score
   */
  private searchWordsInText(query: string, text: string): number {
    const queryLower = query.toLowerCase().trim();
    const words = text.toLowerCase().split(/\s+/);

    let bestScore = 0;

    for (const word of words) {
      const score = this.fuzzyMatchScore(queryLower, word);
      bestScore = Math.max(bestScore, score);
    }

    return bestScore;
  }

  /**
   * Search for tickers matching the query strings
   * @param args Configuration options
   * @param args.queries List of search strings to match against ticker symbols or names
   * @param args.limit Maximum number of results to return (default: 10, max: 10)
   * @returns JSON string with list of matching tickers
   */
  async search_dataset(args: {
    queries: string[];
    limit?: number;
  }): Promise<string> {
    try {
      const { queries, limit = 10 } = args;

      if (!queries || queries.length === 0) {
        return JSON.stringify({
          error: 'Queries parameter is required and cannot be empty'
        });
      }

      // Load tickers data lazily
      const tickers = await this.loadTickers();

      // Enforce maximum limit of 10
      const maxLimit = Math.min(limit, 10);

      const allResults: SearchResult[] = [];
      const seenTickers = new Set<string>();

      // Process each query
      for (const query of queries) {
        if (!query || query.trim() === '') {
          continue; // Skip empty queries
        }

        const queryLower = query.toLowerCase().trim();

        // Search through all tickers
        for (const [ticker, data] of Object.entries(tickers)) {
          let bestScore = 0;

          // Try matching against ticker symbol
          const tickerScore = this.fuzzyMatchScore(queryLower, ticker);
          bestScore = Math.max(bestScore, tickerScore);

          // Try matching against company name
          const nameScore = this.fuzzyMatchScore(queryLower, data.name);
          bestScore = Math.max(bestScore, nameScore * 0.8); // Slightly lower weight for name matches

          // Try matching against individual words in company name
          const wordScore = this.searchWordsInText(queryLower, data.name);
          bestScore = Math.max(bestScore, wordScore * 0.7); // Lower weight for word matches

          // Only include results with reasonable scores
          if (bestScore > 30) {
            // Check if we've already seen this ticker from a previous query
            if (!seenTickers.has(ticker)) {
              allResults.push({
                ticker,
                name: data.name,
                type: data.type,
                source: data.source,
                score: Math.round(bestScore)
              });
              seenTickers.add(ticker);
            } else {
              // Update the score if this query found a better match
              const existingResult = allResults.find(r => r.ticker === ticker);
              if (
                existingResult &&
                Math.round(bestScore) > existingResult.score
              ) {
                existingResult.score = Math.round(bestScore);
              }
            }
          }
        }
      }

      // Sort by score (descending) and return top results
      const sortedResults = allResults
        .sort((a, b) => b.score - a.score)
        .slice(0, maxLimit);

      return JSON.stringify(sortedResults);
    } catch (error) {
      console.error('Error searching datasets:', error);
      return JSON.stringify({
        error: `Failed to search datasets: ${error instanceof Error ? error.message : String(error)}`
      });
    }
  }
}

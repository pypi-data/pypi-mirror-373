import regex as re

from typing import Optional

def format_search_query_for_sqlite(search_string : str) -> Optional[str]:
    """
    Converts a search string into a SQLite FTS5 query format with:
    - Split words separated by spaces, with wildcard suffix, can occur anywhere in the text
        e..g 'word1 word2' becomes 'word1* word2*'
    - Words in quotes preserved as exact phrases, with wildcard suffix
        e.g. '"exact phrase" word2 word3' becomes '"exact phrase"* word2* word3*'
    - if a word contains special characters, they are replaced by spaces, and require the right word order
        e.g. 'word1-word2 word3' becomes '"word1 word2"* word3*'
    
    Parameters:
        search_string (str): The input search string
        
    Returns:
        str | None: The formatted query string for use with SQLite FTS, or None if the input is empty
    """
    if not search_string or not search_string.strip():
        return None
    
    # Extract quoted phrases and non-quoted parts
    quote_pattern = r'"([^"]*)"'
    query_parts = []
    last_end = 0
    
    # Find all quoted sections
    for match in re.finditer(quote_pattern, search_string):
        if match.start() > last_end:
            normal_text = search_string[last_end:match.start()].strip()
            if normal_text:
                for word in normal_text.split():
                    query_parts.append(format_fts_single_string(word))
        
        quoted_text = match.group(1)
        if quoted_text:
            query_parts.append(format_fts_single_string(quoted_text))
        
        last_end = match.end()
    
    # Add any remaining text after the last quote
    if last_end < len(search_string):
        remaining_text = search_string[last_end:].strip()
        if remaining_text:
            for word in remaining_text.split():
                query_parts.append(format_fts_single_string(word))
    
    # Combine all parts into a single query, return None if empty
    search_query = ' '.join(query_parts)
    if not search_query.strip():
        return None
    return search_query

def format_fts_single_string(string: str) -> str:
    """
    Removes any special characters by a space, applied quote marks if needed.
    
    Parameters:
        string (str): The input word to process
    
    Returns:
        str: The processed string
    """
    cleaned_word = process_search_words(string)
    
    if not cleaned_word:
        return ''
    
    if ' ' in cleaned_word:
        return f'"{cleaned_word}"*'
    
    return f'{cleaned_word}*'

def process_search_words(words : str) -> str:
    """
    Clears out any special characters from the search helper string and removes any extra spaces.
    
    Parameters:
        words (str): The search helper string to process
    
    Returns:
        str: The cleaned search helper string
    """    
    cleaned_word = re.sub(r'[^\p{L}\d]', ' ', words)
    cleaned_word = re.sub(r'\s+', ' ', cleaned_word)
    return cleaned_word.strip()
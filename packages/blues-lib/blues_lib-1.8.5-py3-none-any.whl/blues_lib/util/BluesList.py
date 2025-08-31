class BluesList(list):

  @classmethod 
  def get_length(cls,strings: list[str]) -> int:
    """
    * Calculates the total length of all valid strings in the provided list.
    * Non-string elements are silently ignored.
    * 
    * @param strings List of objects, strings are processed for length
    * @return Total length of all valid strings combined
    """
    total_length = 0
    for element in strings:
      if isinstance(element, str):
        total_length += len(element)
    return total_length
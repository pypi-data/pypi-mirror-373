import secrets

class Utils:
    
    @staticmethod
    def rand_int_inclusive(min_val: int, max_val: int) -> int:
        """
        Return a random integer N such that min_val <= N <= max_val.
        Uses `secrets.randbelow` which is cryptographically secure.

        Parameters
        ----------
        min_val : int
            Lower bound (inclusive).
        max_val : int
            Upper bound (inclusive).

        Returns
        -------
        int
            Random integer in the specified range.
        """
        if min_val > max_val:
            raise ValueError("min_val must be <= max_val")

        # randbelow(n) returns 0 .. n-1.  We need a window of size (max-min+1)
        range_size = max_val - min_val + 1
        return secrets.randbelow(range_size) + min_val
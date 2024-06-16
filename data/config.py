DELAYS = {
    'ACCOUNT': [5, 15],  # delay between connections to accounts (the more accounts, the longer the delay)
    'PLAY': [5, 15],   # delay between play in seconds
    'ERROR_PLAY': [60, 180],    # delay between errors in the game in seconds
    'CLAIM': [600, 1800]   # delay in seconds before claim points every 8 hours
}

# proxy type for tg client
PROXY_TYPE = "socks5"  # "socks4", "socks5" and "http" are supported

# session folder (do not change)
WORKDIR = "sessions/"

# timeout in seconds for checking accounts on valid
TIMEOUT = 30
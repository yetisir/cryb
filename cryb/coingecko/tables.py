class Coin(sql.Model):
    __tablename__ = 'coin'

    id = sql.Column(sql.String(32), primary_key=True)
    symbol = sql.Column(sql.String(32), nullable=False)
    name = sql.Column(sql.String(32), nullable=False)
    description = sql.Column(sql.String(2048))
    homepage = sql.Column(sql.String(128))
    github = sql.Column(sql.String(128))
    twitter = sql.Column(sql.String(128))
    facebook = sql.Column(sql.String(128))
    reddit = sql.Column(sql.String(128))
    telegram = sql.Column(sql.String(128))


class CoinSocialData(sql.Model):
    __tablename__ = 'coin_social_data'

    timestamp = sql.Column(sql.Date(), primary_key=True)
    coin_id = sql.Column(sql.Integer(), ForeignKey('coin.id'), primary_key=True)
    facebook_likes = sql.Column(sql.Integer(), nullable=False)
    twitter_followers = sql.Column(sql.Integer(), nullable=False)
    reddit_average_posts_48h = sql.Column(sql.Integer(), nullable=False)
    reddit_avergage_comments_48h = sql.Column(sql.Integer(), nullable=False)
    reddit_subscribers = sql.Column(sql.Integer(), nullable=False)
    reddit_accounts_active_48h = sql.Column(sql.Integer(), nullable=False)


class CoinDeveloperData(sql.Model):
    __tablename__ = 'coin_developer_data'

    timestamp = sql.Column(sql.Date(), primary_key=True)
    coin_id = sql.Column(sql.Integer(), ForeignKey('coin.id'), primary_key=True)
    forks = sql.Column(sql.Integer(), nullable=False)
    stars = sql.Column(sql.Integer(), nullable=False)
    subscribers = sql.Column(sql.Integer(), nullable=False)
    total_issues = sql.Column(sql.Integer(), nullable=False)
    closed_issues = sql.Column(sql.Integer(), nullable=False)
    pull_requests_merged = sql.Column(sql.Integer(), nullable=False)
    pull_request_contributors = sql.Column(sql.Integer(), nullable=False)
    code_additions_4_weeks = sql.Column(sql.Integer(), nullable=False)
    code_deletions_4_weeks = sql.Column(sql.Integer(), nullable=False)
    commit_count_4_weeks = sql.Column(sql.Integer(), nullable=False)

class CoinPublicInterestData(sql.Model):
    __tablename__ = 'coin_public_interest_data'

    timestamp = sql.Column(sql.Date(), primary_key=True)
    coin_id = sql.Column(sql.Integer(), ForeignKey('coin.id'), primary_key=True)
    alexa_rank = sql.Column(sql.Integer(), nullable=False)
    bing_matches = sql.Column(sql.Integer(), nullable=False)


class CoinMarketData(sql.Model):
    __tablename__ = 'coin_market_data'

    timestamp = sql.Column(sql.Date(), primary_key=True)
    coin_id = sql.Column(sql.Integer(), ForeignKey('coin.id'), primary_key=True)
    price_usd = sql.Column(sql.Float, nullable=False)



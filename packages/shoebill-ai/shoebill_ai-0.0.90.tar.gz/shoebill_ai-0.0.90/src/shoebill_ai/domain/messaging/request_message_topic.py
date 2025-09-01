from enum import Enum


class RequestMessageTopic(str, Enum):
    """
    Represents a collection of predefined topics as an enumeration.

    This class is an enumeration that defines constant string values for use
    as topic identifiers. These topics represent specific actions or messages
    within a messaging or vector database management context. It ensures
    consistent usage of these predefined topics across the application.

    syntax: [hai].[source].[destination].[action]

    """
    # Telegram
    TG_CHAT_SEND = "hai.tg.chat.send"
    TG_USER_CHAT_SEND = "hai.tg.user.chat.send"
    TG_CHAT_REPLY = "hai.tg.chat.reply"

    # vector database
    VECTORS_SAVE = "hai.vectors.save"

    VECTORS_QUERY = "hai.vectors.query"
    VECTORS_QUERY_RESPONSE = "hai.vectors.query.response"

    VECTORS_METADATA_READ = "hai.vectors.metadata.read"
    VECTORS_METADATA_READ_RESPONSE = "hai.vectors.metadata.read.response"

    # Twitter
    TWITTER_GET_USER = "hai.twitter.get.user"
    TWITTER_GET_USER_RESPONSE = "hai.twitter.get.user.response"
    TWITTER_GET_USERS = "hai.twitter.get.users"
    TWITTER_GET_USERS_RESPONSE = "hai.twitter.get.users.response"
    TWITTER_GET_USER_TWEETS = "hai.twitter.get.user.tweets"
    TWITTER_GET_USER_TWEETS_RESPONSE = "hai.twitter.get.user.tweets.response"

    TWITTER_USER_SEND_AI_CHAT_SEND = "hai.twitter.user.chat.send"
    TWITTER_USER_SEND_AI_CHAT_SEND_RESPONSE = "hai.twitter.user.chat.send.response"

    TWITTER_FOLLOW_USER= "hai.twitter.follow.user"
    TWITTER_FOLLOW_USER_RESPONSE = "hai.twitter.follow.user.response"

    TWITTER_GET_HOME_TIMELINE= "hai.twitter.get.home.timeline"
    TWITTER_GET_HOME_TIMELINE_RESPONSE = "hai.twitter.get.home.timeline.response"

    TWITTER_RETWEET= "hai.twitter.retweet"
    TWITTER_RETWEET_RESPONSE = "hai.twitter.retweet.response"

    TWITTER_REPLY= "hai.twitter.reply"
    TWITTER_REPLY_RESPONSE = "hai.twitter.reply.response"

    TWITTER_POST_TWEET= "hai.twitter.post.tweet"
    TWITTER_POST_TWEET_RESPONSE = "hai.twitter.post.tweet.response"
    
    TWITTER_POST_TWEET_WITH_MEDIA = "hai.twitter.post.tweet.with.media"
    TWITTER_POST_TWEET_WITH_MEDIA_RESPONSE = "hai.twitter.post.tweet.with.media.response"

    TWITTER_QUOTE_RETWEET= "hai.twitter.quote.retweet"
    TWITTER_QUOTE_RETWEET_RESPONSE = "hai.twitter.quote.retweet.response"

    TWITTER_GET_TWEET= "hai.twitter.get.tweet"
    TWITTER_GET_TWEET_RESPONSE = "hai.twitter.get.tweet.response"

    TWITTER_SEARCH= "hai.twitter.search"
    TWITTER_SEARCH_RESPONSE = "hai.twitter.search.response"

    TWITTER_GET_REPLIES_AND_MENTIONS = "hai.twitter.get.replies.and.mentions"
    TWITTER_GET_REPLIES_AND_MENTIONS_RESPONSE = "hai.twitter.get.replies.and.mentions.response"

    # tools
    WEB_SEARCH = "hai.tools.web.search"
    WEB_SEARCH_RESPONSE = "hai.tools.web.search.response"

    WEB_GET_DOCS = "hai.tools.web.get.docs"
    WEB_GET_DOCS_RESPONSE = "hai.tools.web.get.docs.response"

    WEB_FIND_RELATED = "hai.tools.web.find.related"
    WEB_FIND_RELATED_RESPONSE = "hai.tools.web.find.related.response"

    WEB_GET_TWITTER_PROFILES= "hai.tools.web.get.twitter.profiles"
    WEB_GET_TWITTER_PROFILES_RESPONSE = "hai.tools.web.get.twitter.profiles.response"

    INIT_KNOWLEDGE_BASE = "hai.tools.init.knowledge.base"
    INIT_KNOWLEDGE_BASE_RESPONSE = "hai.tools.init.knowledge.base.response"

    # graph database
    GRAPH_NODE_ADD = "hai.graph.node.add"
    GRAPH_NODE_UPDATE = "hai.graph.node.update"
    GRAPH_NODE_GET = "hai.graph.node.get"
    GRAPH_NODE_DELETE = "hai.graph.node.delete"
    GRAPH_RELATIONSHIP_ADD = "hai.graph.relationship.add"
    GRAPH_RELATIONSHIP_DELETE = "hai.graph.relationship.delete"
    GRAPH_QUERY = "hai.graph.query"
    GRAPH_CLEAR = "hai.graph.clear"
    GRAPH_GET_ALL = "hai.graph.get.all"
    GRAPH_NODES_BY_PROPERTY = "hai.graph.nodes.by.property"
    GRAPH_RELATIONSHIPS_BY_TYPE = "hai.graph.relationships.by.type"
    GRAPH_RELATIONSHIPS_BETWEEN_NODES = "hai.graph.relationships.between.nodes"
    GRAPH_OUTGOING_RELATIONSHIPS = "hai.graph.outgoing.relationships"
    GRAPH_INCOMING_RELATIONSHIPS = "hai.graph.incoming.relationships"
    GRAPH_NODES_BY_LABEL = "hai.graph.nodes.by.label"
    GRAPH_NODE_INFO = "hai.graph.node.info"
    GRAPH_FIND_RELATED_NODES = "hai.graph.find.related.nodes"
    GRAPH_COUNT_RELATIONSHIPS = "hai.graph.count.relationships"
    GRAPH_PATHS = "hai.graph.paths"
    GRAPH_ANNOUNCEMENT_NODES_SINCE_TIMESTAMP = "hai.graph.announcement.nodes.since.timestamp"
    GRAPH_EVENT_NODES_SINCE_TIMESTAMP = "hai.graph.event.nodes.since.timestamp"
    GRAPH_OPINION_NODES_SINCE_TIMESTAMP = "hai.graph.opinion.nodes.since.timestamp"
    GRAPH_NODE_SUBGRAPH = "hai.graph.node.subgraph"
    GRAPH_FIND_OPINIONS_ON_NODE = "hai.graph.find.opinions.on.node"
    GRAPH_FIND_RELATIONS_BETWEEN_ENTITIES = "hai.graph.find.relations.between.entities"
    GRAPH_TRACE_CLAIM_SOURCE = "hai.graph.trace.claim.source"
    GRAPH_TRACE_NODE_SOURCE = "hai.graph.trace.node.source"
    GRAPH_FIND_USER_EVENTS_AND_ANNOUNCEMENTS = "hai.graph.find.user.events.and.announcements"
    GRAPH_GET_STATISTICS = "hai.graph.get.statistics"

    GRAPH_QUERY_OPERATION = "hai.graph.query.operation"
    GRAPH_QUERY_OPERATION_RESPONSE = "hai.graph.query.operation.response"

    GRAPH_NODE_ADD_RESPONSE = "hai.graph.node.add.response"
    GRAPH_NODE_UPDATE_RESPONSE = "hai.graph.node.update.response"
    GRAPH_NODE_GET_RESPONSE = "hai.graph.node.get.response"
    GRAPH_RELATIONSHIP_ADD_RESPONSE = "hai.graph.relationship.add.response"
    GRAPH_QUERY_RESPONSE = "hai.graph.query.response"
    GRAPH_CLEAR_RESPONSE = "hai.graph.clear.response"
    GRAPH_GET_ALL_RESPONSE = "hai.graph.get.all.response"
    GRAPH_NODES_BY_PROPERTY_RESPONSE = "hai.graph.nodes.by.property.response"
    GRAPH_RELATIONSHIPS_BY_TYPE_RESPONSE = "hai.graph.relationships.by.type.response"
    GRAPH_RELATIONSHIPS_BETWEEN_NODES_RESPONSE = "hai.graph.relationships.between.nodes.response"
    GRAPH_OUTGOING_RELATIONSHIPS_RESPONSE = "hai.graph.outgoing.relationships.response"
    GRAPH_INCOMING_RELATIONSHIPS_RESPONSE = "hai.graph.incoming.relationships.response"
    GRAPH_NODES_BY_LABEL_RESPONSE = "hai.graph.nodes.by.label.response"
    GRAPH_NODE_INFO_RESPONSE = "hai.graph.node.info.response"
    GRAPH_FIND_RELATED_NODES_RESPONSE = "hai.graph.find.related.nodes.response"
    GRAPH_COUNT_RELATIONSHIPS_RESPONSE = "hai.graph.count.relationships.response"
    GRAPH_PATHS_RESPONSE = "hai.graph.paths.response"
    GRAPH_ANNOUNCEMENT_NODES_SINCE_TIMESTAMP_RESPONSE = "hai.graph.announcement.nodes.since.timestamp.response"
    GRAPH_EVENT_NODES_SINCE_TIMESTAMP_RESPONSE = "hai.graph.event.nodes.since.timestamp.response"
    GRAPH_OPINION_NODES_SINCE_TIMESTAMP_RESPONSE = "hai.graph.opinion.nodes.since.timestamp.response"
    GRAPH_NODE_SUBGRAPH_RESPONSE = "hai.graph.node.subgraph.response"
    GRAPH_FIND_OPINIONS_ON_NODE_RESPONSE = "hai.graph.find.opinions.on.node.response"
    GRAPH_FIND_RELATIONS_BETWEEN_ENTITIES_RESPONSE = "hai.graph.find.relations.between.entities.response"
    GRAPH_TRACE_CLAIM_SOURCE_RESPONSE = "hai.graph.trace.claim.source.response"
    GRAPH_TRACE_NODE_SOURCE_RESPONSE = "hai.graph.trace.node.source.response"
    GRAPH_FIND_USER_EVENTS_AND_ANNOUNCEMENTS_RESPONSE = "hai.graph.find.user.events.and.announcements.response"
    GRAPH_GET_STATISTICS_RESPONSE = "hai.graph.get.statistics.response"

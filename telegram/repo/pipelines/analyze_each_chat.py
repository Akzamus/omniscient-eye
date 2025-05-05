def pipline(chat_ids: list[int], participant_types: list[str] | None = None) -> list[dict]:
    match_stage = {
        "chat_id": {"$in": chat_ids}
    }

    if participant_types:
        match_stage["type"] = {"$in": participant_types}

    return [
        {
            "$match": match_stage
        },
        {
            "$group": {
                "_id": "$chat_id",
                "distinct_users": {"$addToSet": "$user_id"},
                "types": {"$push": "$type"},
                "recommendations": {"$push": "$recommendation"}
            }
        },
        {
            "$project": {
                "chat_id": "$_id",
                "active_participant_count": {"$size": "$distinct_users"},
                "participant_type_counts": {
                    "$arrayToObject": {
                        "$map": {
                            "input": {
                                "$sortArray": {
                                    "input": {
                                        "$map": {
                                            "input": {"$setUnion": ["$types", []]},
                                            "as": "t",
                                            "in": {
                                                "k": {"$toString": "$$t"},
                                                "v": {
                                                    "$size": {
                                                        "$filter": {
                                                            "input": "$types",
                                                            "as": "tt",
                                                            "cond": {"$eq": ["$$tt", "$$t"]}
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                    },
                                    "sortBy": {"v": -1}
                                }
                            },
                            "as": "item",
                            "in": {"k": "$$item.k", "v": "$$item.v"}
                        }
                    }
                },
                "recommendation_counts": {
                    "$arrayToObject": {
                        "$map": {
                            "input": {
                                "$sortArray": {
                                    "input": {
                                        "$map": {
                                            "input": {"$setUnion": ["$recommendations", []]},
                                            "as": "r",
                                            "in": {
                                                "k": {"$toString": "$$r"},
                                                "v": {
                                                    "$size": {
                                                        "$filter": {
                                                            "input": "$recommendations",
                                                            "as": "rr",
                                                            "cond": {"$eq": ["$$rr", "$$r"]}
                                                        }
                                                    }
                                                },
                                                "numKey": {"$toInt": "$$r"}
                                            }
                                        }
                                    },
                                    "sortBy": {"numKey": -1}
                                }
                            },
                            "as": "item",
                            "in": {"k": "$$item.k", "v": "$$item.v"}
                        }
                    }
                }
            }
        }
    ]

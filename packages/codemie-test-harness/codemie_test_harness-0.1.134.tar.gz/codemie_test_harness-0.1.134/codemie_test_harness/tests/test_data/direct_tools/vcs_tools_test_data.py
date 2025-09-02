from codemie_test_harness.tests.enums.tools import VcsTool, Toolkit


vcs_tools_test_data = [
    (
        Toolkit.VCS,
        VcsTool.GITHUB,
        {
            "query": {
                "method": "GET",
                "url": "https://api.github.com/repos/wild47/final_task/issues/5",
                "method_arguments": {},
                "custom_headers": {},
            }
        },
        """
            {
              "url" : "https://api.github.com/repos/wild47/final_task/issues/5",
              "repository_url" : "https://api.github.com/repos/wild47/final_task",
              "labels_url" : "https://api.github.com/repos/wild47/final_task/issues/5/labels{/name}",
              "comments_url" : "https://api.github.com/repos/wild47/final_task/issues/5/comments",
              "events_url" : "https://api.github.com/repos/wild47/final_task/issues/5/events",
              "html_url" : "https://github.com/wild47/final_task/issues/5",
              "id" : 2790235989,
              "node_id" : "I_kwDODfBHGs6mT59V",
              "number" : 5,
              "title" : "Test",
              "user" : {
                "login" : "wild47",
                "id" : 54711118,
                "node_id" : "MDQ6VXNlcjU0NzExMTE4",
                "avatar_url" : "https://avatars.githubusercontent.com/u/54711118?v=4",
                "gravatar_id" : "",
                "url" : "https://api.github.com/users/wild47",
                "html_url" : "https://github.com/wild47",
                "followers_url" : "https://api.github.com/users/wild47/followers",
                "following_url" : "https://api.github.com/users/wild47/following{/other_user}",
                "gists_url" : "https://api.github.com/users/wild47/gists{/gist_id}",
                "starred_url" : "https://api.github.com/users/wild47/starred{/owner}{/repo}",
                "subscriptions_url" : "https://api.github.com/users/wild47/subscriptions",
                "organizations_url" : "https://api.github.com/users/wild47/orgs",
                "repos_url" : "https://api.github.com/users/wild47/repos",
                "events_url" : "https://api.github.com/users/wild47/events{/privacy}",
                "received_events_url" : "https://api.github.com/users/wild47/received_events",
                "type" : "User",
                "user_view_type" : "public",
                "site_admin" : false
              },
              "labels" : [ ],
              "state" : "open",
              "locked" : false,
              "assignee" : null,
              "assignees" : [ ],
              "milestone" : null,
              "comments" : 0,
              "created_at" : "2025-01-15T16:01:17Z",
              "updated_at" : "2025-01-15T16:01:17Z",
              "closed_at" : null,
              "author_association" : "OWNER",
              "active_lock_reason" : null,
              "sub_issues_summary" : {
                "total" : 0,
                "completed" : 0,
                "percent_completed" : 0
              },
              "issue_dependencies_summary" : {
                "blocked_by" : 0,
                "total_blocked_by" : 0,
                "blocking" : 0,
                "total_blocking" : 0
              },
              "body" : "This is a test issue.",
              "closed_by" : null,
              "reactions" : {
                "url" : "https://api.github.com/repos/wild47/final_task/issues/5/reactions",
                "total_count" : 0,
                "+1" : 0,
                "-1" : 0,
                "laugh" : 0,
                "hooray" : 0,
                "confused" : 0,
                "heart" : 0,
                "rocket" : 0,
                "eyes" : 0
              },
              "timeline_url" : "https://api.github.com/repos/wild47/final_task/issues/5/timeline",
              "performed_via_github_app" : null,
              "state_reason" : null
            }
        """,
    ),
    (
        Toolkit.VCS,
        VcsTool.GITLAB,
        {
            "query": {
                "method": "GET",
                "url": "/api/v4/projects/17889/merge_requests/7014",
                "method_arguments": {},
            }
        },
        """
            HTTP: GET https://gitbud.epam.com//api/v4/projects/17889/merge_requests/7014 -> 
            200 OK {"id":342087,"iid":7014,"project_id":17889,"title":"sdk_juhigsaqwkedvdy",
            "description":"Merge the changes in branch sdk_cgkbdhekvjiolpi to the main branch, including the creation 
            of SdkYmsodrhepphxpyl.java with 'Hello World'.","state":"closed","created_at":"2025-08-08T08:23:05.433Z",
            "updated_at":"2025-08-08T08:23:22.442Z","merged_by":null,"merge_user":null,"merged_at":null,
            "closed_by":{"id":23454,"username":"anton_yeromin","name":"Anton Yeromin","state":"active",
            "locked":false,"avatar_url":"https://gitbud.epam.com/uploads/-/system/user/avatar/23454/avatar.png",
            "web_url":"https://gitbud.epam.com/anton_yeromin"},"closed_at":"2025-08-08T08:23:22.499Z",
            "target_branch":"main","source_branch":"sdk_cgkbdhekvjiolpi","user_notes_count":0,"upvotes":0,
            "downvotes":0,"author":{"id":23454,"username":"anton_yeromin","name":"Anton Yeromin","state":"active",
            "locked":false,"avatar_url":"https://gitbud.epam.com/uploads/-/system/user/avatar/23454/avatar.png",
            "web_url":"https://gitbud.epam.com/anton_yeromin"},"assignees":[],"assignee":null,"reviewers":[],
            "source_project_id":17889,"target_project_id":17889,"labels":["created-by-agent"],"draft":false,
            "imported":false,"imported_from":"none","work_in_progress":false,"milestone":null,
            "merge_when_pipeline_succeeds":false,"merge_status":"can_be_merged","detailed_merge_status":
            "not_open","merge_after":null,"sha":"ea596c39f296ce22843c094bffc703e892780586",
            "merge_commit_sha":null,"squash_commit_sha":null,"discussion_locked":null,
            "should_remove_source_branch":null,"force_remove_source_branch":null,
            "prepared_at":"2025-08-08T08:23:07.437Z","reference":"!7014","references":
            {"short":"!7014","relative":"!7014","full":"epm-cdme/autotests/codemie-test-project!7014"},
            "web_url":"https://gitbud.epam.com/epm-cdme/autotests/codemie-test-project/-/merge_requests/7014",
            "time_stats":{"time_estimate":0,"total_time_spent":0,"human_time_estimate":null,
            "human_total_time_spent":null},"squash":false,"squash_on_merge":false,"task_completion_status":{
            "count":0,"completed_count":0},"has_conflicts":false,"blocking_discussions_resolved":true,
            "subscribed":true,"changes_count":"1","latest_build_started_at":null,"latest_build_finished_at":null,
            "first_deployed_to_production_at":null,"pipeline":null,"head_pipeline":null,"diff_refs":{"base_sha":
            "22790383a6ca08ae66b3a9e005707122d803407e","head_sha":"ea596c39f296ce22843c094bffc703e892780586",
            "start_sha":"22790383a6ca08ae66b3a9e005707122d803407e"},"merge_error":null,"first_contribution":
            true,"user":{"can_merge":true}}
        
        """,
    ),
]

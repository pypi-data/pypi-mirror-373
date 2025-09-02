from codemie_test_harness.tests.enums.tools import Toolkit, ProjectManagementTool
from codemie_test_harness.tests.utils.constants import ProjectManagementIntegrationType

project_management_tools_data = [
    (
        Toolkit.PROJECT_MANAGEMENT,
        ProjectManagementTool.JIRA,
        ProjectManagementIntegrationType.JIRA,
        {"method": "GET", "relative_url": "/rest/api/2/issue/EPMCDME-222"},
        """
            HTTP: GET /rest/api/2/issue/EPMCDME-222 -> 200 OK {"expand":"renderedFields,names,schema,operations,editmeta,
            changelog,versionedRepresentations","id":"6959493","self":"https://jiraeu.epam.com/rest/api/2/issue/6959493",
            "key":"EPMCDME-222","fields":{"customfield_38400":null,"customfield_38401":null,"customfield_38402":null,
            "customfield_34834":null,"customfield_38403":null,"resolution":{"self":"https://jiraeu.epam.com/rest/api/2/
            resolution/18","id":"18","description":"Resolution if a task or defect is no longer valid based on changes in
            the system or requirements","name":"Obsolete"},"customfield_38404":null,"customfield_17702":null,"customfield_
            38405":null,"customfield_38406":null,"customfield_32300":null,"customfield_22601":null,"lastViewed":null,"
            customfield_38410":null,"labels":["CodeMie"],"customfield_17811":null,"customfield_33400":null,"customfield_
            11700":null,"customfield_35700":null,"customfield_38407":null,"customfield_13206":"1.\r\n2.\r\n3.\r\n4.","
            customfield_34732":null,"customfield_38408":null,"customfield_38409":null,"customfield_11701":null,"
            aggregatetimeoriginalestimate":null,"issuelinks":[],"assignee":{"self":"https://jiraeu.epam.com/rest/api/2/user
            ?username=Vadym_Vlasenko%40epam.com","name":"Vadym_Vlasenko@epam.com","key":"vadym_vlasenko","emailAddress":"
            Vadym_Vlasenko@epam.com","avatarUrls":{"48x48":"https://jiraeu.epam.com/secure/useravatar?ownerId=vadym_
            vlasenko&avatarId=82922","24x24":"https://jiraeu.epam.com/secure/useravatar?size=small&ownerId=vadym_vlasenko&
            avatarId=82922","16x16":"https://jiraeu.epam.com/secure/useravatar?size=xsmall&ownerId=vadym_vlasenko&avatarId=
            82922","32x32":"https://jiraeu.epam.com/secure/useravatar?size=medium&ownerId=vadym_vlasenko&avatarId=82922"},
            "displayName":"Vadym Vlasenko","active":true,"timeZone":"Etc/GMT"},"components":[],"customfield_31900":null,"
            customfield_15500":null,"customfield_35706":null,"customfield_35705":null,"customfield_34859":null,"customfield_
            35704":null,"customfield_35703":null,"customfield_35702":null,"customfield_15501":null,"customfield_17800":null,
            "customfield_35701":null,"customfield_32200":null,"customfield_36800":null,"customfield_35710":null,"customfield_
            32202":null,"customfield_32201":null,"customfield_30704":null,"subtasks":[],"reporter":{"self":"https://jiraeu.
            epam.com/rest/api/2/user?username=Yana_Kharchenko%40epam.com","name":"Yana_Kharchenko@epam.com","key":"iana_gurska
            ","emailAddress":"Yana_Kharchenko@epam.com","avatarUrls":{"48x48":"https://jiraeu.epam.com/secure/useravatar?
            ownerId=iana_gurska&avatarId=82512","24x24":"https://jiraeu.epam.com/secure/useravatar?size=small&ownerId=iana_
            gurska&avatarId=82512","16x16":"https://jiraeu.epam.com/secure/useravatar?size=xsmall&ownerId=iana_gurska&
            avatarId=82512","32x32":"https://jiraeu.epam.com/secure/useravatar?size=medium&ownerId=iana_gurska&avatarId=
            82512"},"displayName":"Yana Kharchenko","active":true,"timeZone":"Europe/Kiev"},"customfield_32204":null,
            "customfield_32203":null,"customfield_35720":null,"customfield_11801":null,"customfield_34873":null,"progress":
            {"progress":0,"total":0},"votes":{"self":"https://jiraeu.epam.com/rest/api/2/issue/EPMCDME-222/votes","votes":0,
            "hasVoted":false},"worklog":{"startAt":0,"maxResults":20,"total":0,"worklogs":[]},"archivedby":null,"issuetype":
            {"self":"https://jiraeu.epam.com/rest/api/2/issuetype/6","id":"6","description":"Created by Jira Software - do
            not edit or delete. Issue type for a big user story that needs to be broken down.","iconUrl":"https://jiraeu.
            epam.com/secure/viewavatar?size=xsmall&avatarId=44407&avatarType=issuetype","name":"Epic","subtask":false,
            "avatarId":44407},"project":{"self":"https://jiraeu.epam.com/rest/api/2/project/79608","id":"79608","key":
            "EPMCDME","name":"EPM-CDME","projectTypeKey":"software","avatarUrls":{"48x48":"https://jiraeu.epam.com/secure/
            projectavatar?avatarId=59003","24x24":"https://jiraeu.epam.com/secure/projectavatar?size=small&avatarId=59003",
            "16x16":"https://jiraeu.epam.com/secure/projectavatar?size=xsmall&avatarId=59003","32x32":"https://jiraeu.epam.
            com/secure/projectavatar?size=medium&avatarId=59003"}},"customfield_11000":null,"customfield_15602":null,
            "customfield_13301":null,"customfield_34885":null,"customfield_34401":"0.0","customfield_34402":"0.0","customfield
            _14504":null,"customfield_34400":null,"customfield_26100":null,"resolutiondate":"2024-06-21T23:10:11.256+0000","
            customfield_26102":null,"customfield_30609":null,"customfield_32908":null,"watches":{"self":"https://jiraeu.epam.
            com/rest/api/2/issue/EPMCDME-222/watchers","watchCount":1,"isWatching":false},"customfield_32905":null,"customfield
            _30605":null,"customfield_30606":null,"customfield_32904":null,"customfield_23518":null,"customfield_32907":null,
            \"customfield_30607":null,"customfield_32906":null,"customfield_30601":null,"customfield_30602":null,"customfield_
            32903":null,"customfield_12200":null,"customfield_30603":null,"customfield_32902":null,"customfield_30604":null,"
            customfield_34405":{"self":"https://jiraeu.epam.com/rest/api/2/customFieldOption/50316","value":"Undefined","id":
            "50316","disabled":false},"customfield_14502":{"self":"https://jiraeu.epam.com/rest/api/2/customFieldOption/12805"
            ,"value":"Done","id":"12805","disabled":false},"customfield_14503":null,"customfield_14500":null,"customfield_12203
            ":null,"customfield_30600":null,"customfield_14501":"CodeMie: Large datasets and multiple knowledge bases",
            "customfield_33323":null,"customfield_33200":null,"customfield_11900":null,"customfield_34895":null,"customfield_
            37004":null,"customfield_37000":null,"updated":"2025-08-01T18:21:21.420+0000","customfield_25700":"2|hjyh9b:","
            customfield_30616":null,"customfield_30617":null,"customfield_16110":null,"customfield_30618":null,"
            timeoriginalestimate":null,"customfield_30612":null,"customfield_38102":null,"description":null,"customfield_
            31701":null,"customfield_30613":null,"customfield_32911":null,"customfield_30614":null,"customfield_38104":null,
            "customfield_38105":null,"customfield_19501":null,"customfield_38106":null,"customfield_38107":null,"customfield_
            31700":null,"customfield_33325":null,"customfield_34898":{"self":"https://jiraeu.epam.com/rest/api/2/customFieldO
            ption/51124","value":"No","id":"51124","disabled":false},"customfield_30610":null,"customfield_38108":null,"
            customfield_34899":{"self":"https://jiraeu.epam.com/rest/api/2/customFieldOption/51126","value":"No","id":"51126",
            "disabled":false},"timetracking":{},"customfield_30611":null,"customfield_38109":null,"customfield_10005":null,"
            customfield_34302":null,"customfield_34423":{"self":"https://jiraeu.epam.com/rest/api/2/customFieldOption/50322",
            "value":"Emakina","id":"50322","disabled":false},"customfield_33334":["Vadym_Vlasenko@epam.com(vadym_vlasenko)","
            Yana_Kharchenko@epam.com(iana_gurska)"],"customfield_15816":"0.0","customfield_34545":null,"customfield_33335":
            null,"customfield_34300":null,"customfield_10800":"9223372036854775807","customfield_34422":{"self":"https://jiraeu
            .epam.com/rest/api/2/customFieldOption/50320","value":"No","id":"50320","disabled":false},"customfield_34301":null,
            "customfield_33333":"9223372036854775807","customfield_34541":null,"customfield_22900":null,"customfield_20600":
            null,"summary":"CodeMie: Work with large datasets and multiple knowledge bases","customfield_38110":null,"
            customfield_38111":null,"customfield_38112":null,"customfield_30502":null,"customfield_38113":null,"customfield_
            30503":null,"customfield_38114":null,"customfield_38115":null,"customfield_38116":null,"customfield_10001":null,"
            customfield_38117":null,"customfield_34549":null,"customfield_10002":null,"customfield_38118":null,"customfield_
            30500":null,"customfield_33336":{"self":"https://jiraeu.epam.com/rest/api/2/customFieldOption/45742","value":"Open
            ","id":"45742","disabled":false},"customfield_34546":null,"customfield_38119":null,"customfield_10004":null,"
            customfield_34547":null,"customfield_34556":null,"customfield_34553":null,"environment":null,"customfield_33100":"
            N/A","duedate":null,"comment":{"comments":[],"maxResults":0,"total":0,"startAt":0},"customfield_15121":null,"
            customfield_38120":null,"customfield_38122":null,"customfield_15120":null,"customfield_38123":null,"customfield_
            38124":null,"customfield_17303":null,"customfield_38125":null,"customfield_38126":null,"fixVersions":[],"
            customfield_38127":null,"customfield_15129":null,"customfield_38128":null,"customfield_11200":null,"customfield_
            38129":null,"customfield_31600":"","customfield_21912":null,"customfield_38130":null,"customfield_32707":null,"
            customfield_38131":null,"customfield_32706":null,"customfield_38132":null,"customfield_39100":null,"customfield_
            38133":null,"customfield_38134":null,"customfield_15114":null,"customfield_32703":null,"customfield_38135":null,
            "customfield_32702":null,"customfield_38136":null,"customfield_32705":null,"customfield_38137":null,"customfield_
            32704":null,"customfield_38138":null,"priority":{"self":"https://jiraeu.epam.com/rest/api/2/priority/3","iconUrl":
            "https://jiraeu.epam.com/images/icons/priorities/major.svg","name":"Major","id":"3"},"customfield_38139":null,"
            customfield_30400":"{summaryBean=com.atlassian.jira.plugin.devstatus.rest.SummaryBean@1f97334[summary={pullrequest=
            com.atlassian.jira.plugin.devstatus.rest.SummaryItemBean@38fa97ec[overall=PullRequestOverallBean{stateCount=0,
            state='OPEN', details=PullRequestOverallDetails{openCount=0, mergedCount=0, declinedCount=0}},byInstanceType={}],
             build=com.atlassian.jira.plugin.devstatus.rest.SummaryItemBean@55e68473[overall=com.atlassian.jira.plugin.
             devstatus.summary.beans.BuildOverallBean@394f2cd4[failedBuildCount=0,successfulBuildCount=0,unknownBuildCount=0,
             count=0,lastUpdated=<null>,lastUpdatedTimestamp=<null>],byInstanceType={}], review=com.atlassian.jira.plugin.
             devstatus.rest.SummaryItemBean@7307fb9d[overall=com.atlassian.jira.plugin.devstatus.summary.beans.ReviewsOverall
             Bean@d1656dc[stateCount=0,state=<null>,dueDate=<null>,overDue=false,count=0,lastUpdated=<null>,
             lastUpdatedTimestamp=<null>],byInstanceType={}], deployment-environment=com.atlassian.jira.plugin.devstatus.rest.
             SummaryItemBean@6c329e11[overall=com.atlassian.jira.plugin.devstatus.summary.beans.DeploymentOverallBean@2c5b36cf
             [topEnvironments=[],showProjects=false,successfulCount=0,count=0,lastUpdated=<null>,lastUpdatedTimestamp=<null>],
             byInstanceType={}], repository=com.atlassian.jira.plugin.devstatus.rest.SummaryItemBean@60ccfbca[overall=com.
             atlassian.jira.plugin.devstatus.summary.beans.CommitOverallBean@5f53e1b9[count=0,lastUpdated=<null>,
             lastUpdatedTimestamp=<null>],byInstanceType={}], branch=com.atlassian.jira.plugin.devstatus.rest.SummaryItem
             Bean@27693e54[overall=com.atlassian.jira.plugin.devstatus.summary.beans.BranchOverallBean@52718938[count=0,
             lastUpdated=<null>,lastUpdatedTimestamp=<null>],byInstanceType={}]},errors=[],configErrors=[]], devSummary
             Json={\"cachedValue\":{\"errors\":[],\"configErrors\":[],\"summary\":{\"pullrequest\":{\"overall\":{\"count\":
             0,\"lastUpdated\":null,\"stateCount\":0,\"state\":\"OPEN\",\"details\":{\"openCount\":0,\"mergedCount\":0,\"
             declinedCount\":0,\"total\":0},\"open\":true},\"byInstanceType\":{}},\"build\":{\"overall\":{\"count\":0,\"
             lastUpdated\":null,\"failedBuildCount\":0,\"successfulBuildCount\":0,\"unknownBuildCount\":0},\"byInstanceType\":
             {}},\"review\":{\"overall\":{\"count\":0,\"lastUpdated\":null,\"stateCount\":0,\"state\":null,\"dueDate\":null,
             \"overDue\":false,\"completed\":false},\"byInstanceType\":{}},\"deployment-environment\":{\"overall\":{\"count\":
             0,\"lastUpdated\":null,\"topEnvironments\":[],\"showProjects\":false,\"successfulCount\":0},\"byInstanceType\":{}}
             ,\"repository\":{\"overall\":{\"count\":0,\"lastUpdated\":null},\"byInstanceType\":{}},\"branch\":{\"overall\":
             {\"count\":0,\"lastUpdated\":null},\"byInstanceType\":{}}}},\"isStale\":true}}","customfield_35546":null,
             "customfield_33002":null,"customfield_15109":null,"customfield_35785":null,"timeestimate":null,"versions":[],
             "customfield_35540":null,"customfield_14817":null,"customfield_21901":null,"customfield_25500":null,"status":
             {"self":"https://jiraeu.epam.com/rest/api/2/status/6","description":"The issue is considered finished, the
             resolution is correct. Issues which are closed can be reopened.","iconUrl":"https://jiraeu.epam.com/images/icons
             /statuses/closed.png","name":"Closed","id":"6","statusCategory":{"self":"https://jiraeu.epam.com/rest/api/2/
             statuscategory/3","id":3,"key":"done","colorName":"success","name":"Done"}},"customfield_27804":null,"customfield_
             38140":null,"customfield_33803":null,"customfield_35308":null,"customfield_35548":null,"archiveddate":null,"
             customfield_35553":null,"aggregatetimeestimate":null,"customfield_24302":null,"customfield_28902":null,"
             customfield_26603":null,"customfield_26604":null,"customfield_26607":null,"creator":{"self":"https://jiraeu.epam.
             com/rest/api/2/user?username=Yana_Kharchenko%40epam.com","name":"Yana_Kharchenko@epam.com","key":"iana_gurska","
             emailAddress":"Yana_Kharchenko@epam.com","avatarUrls":{"48x48":"https://jiraeu.epam.com/secure/useravatar?
             ownerId=iana_gurska&avatarId=82512","24x24":"https://jiraeu.epam.com/secure/useravatar?size=small&ownerId=iana_
             gurska&avatarId=82512","16x16":"https://jiraeu.epam.com/secure/useravatar?size=xsmall&ownerId=iana_gurska&avatar
             Id=82512","32x32":"https://jiraeu.epam.com/secure/useravatar?size=medium&ownerId=iana_gurska&avatarId=82512"},"
             displayName":"Yana Kharchenko","active":true,"timeZone":"Europe/Kiev"},"customfield_26606":null,"customfield_
             38398":null,"customfield_38399":null,"customfield_34902":"(e.g. 16,6%)","customfield_34903":"(e.g. 100 € /
             hour)","aggregateprogress":{"progress":0,"total":0},"customfield_30300":null,"customfield_34900":{"self":"
             https://jiraeu.epam.com/rest/api/2/customFieldOption/51127","value":"Emakina Group","id":"51127","disabled":
             true},"customfield_34901":"https://share.emakina.net/display/PT/Our+supplier","customfield_30301":null,"
             customfield_18601":null,"customfield_25400":null,"customfield_25401":null,"timespent":null,"customfield_30317":
             null,"customfield_15200":null,"customfield_35208":{"self":"https://jiraeu.epam.com/rest/api/2/customFieldOption/
             52203","value":"All browsers","id":"52203","disabled":false},"customfield_19006":null,"aggregatetimespent":null,"
             customfield_19008":null,"customfield_15205":null,"customfield_35215":null,"customfield_35213":null,"customfield_
             36303":null,"customfield_35214":null,"customfield_30200":null,"customfield_36302":null,"customfield_36300":null,"
             workratio":-1,"customfield_24200":null,"created":"2024-03-07T10:17:49.655+0000","customfield_32505":null,"
             customfield_32506":"1_*:*_1_*:*_9204741626_*|*_6_*:*_1_*:*_0","customfield_35219":{"self":"https://jiraeu.epam.
             com/rest/api/2/customFieldOption/52236","value":"No","id":"52236","disabled":false},"customfield_30201":[],"
             customfield_34801":null,"customfield_36309":null,"customfield_30202":null,"customfield_30203":null,"customfield_
             10300":null,"customfield_34800":null,"customfield_35220":{"self":"https://jiraeu.epam.com/rest/api/2/custom
             FieldOption/52238","value":"EUR","id":"52238","disabled":false},"customfield_35221":"- Boeken\r\n- 
             Bedrijfsstempel\r\n- Fijne stiftjes voor workshops\r\n- Grote meetingroom post it’s\r\n- Schilmesjes\r\n-
              Ladeblokken\r\n- Aangepaste bureaustoel\r\n- Klanten geschenken\r\n- Pizza’s voor pizzasessies\r\n-
              Ontsmettende handgel\r\n- Voetenbankje\r\n- … ","customfield_29900":"0","customfield_34815":null,"
             customfield_34812":"9223372036854775807","customfield_33602":null,"customfield_13004":null,"customfield_33603":
             null,"customfield_15303":null,"customfield_33600":null,"customfield_34931":null,"customfield_33601":null,"
             customfield_17723":null,"customfield_34940":null,"customfield_12701":"1_*:*_1_*:*_9204741626_*|*_6_*:*_1_*:*_0","
             customfield_36327":null,"customfield_12700":null,"customfield_17718":null,"customfield_36202":null,"attachment":[]
             ,"customfield_36681":null,"customfield_30900":null,"customfield_30901":null,"customfield_17715":null,"customfield
             _17713":null,"customfield_27500":null}}
        """,
    ),
    (
        Toolkit.PROJECT_MANAGEMENT,
        ProjectManagementTool.CONFLUENCE,
        ProjectManagementIntegrationType.CONFLUENCE,
        {
            "method": "GET",
            "relative_url": "/rest/api/content/search",
            "params": '{"cql": "title ~ \\"AQA backlog estimation\\"", "limit": 5, "expand": "body.storage"}',
            "is_markdown": False,
        },
        """
        HTTP: GET/rest/api/content/search -> 200OK{"results":[{"id":"2408012834","type":"page","status":"current","title":
        "AQA Backlog Estimation","body":{"storage":{"value":"<p>We've decided to use the following estimation for the test
        cases for AQA:</p><ul style="list-style-type: square;"><li>S - 1h</li><li>M - 3H</li><li>L - 5H</li></ul><p><br /></p><p>
        Approximately estimation for all test cases are:</p><p>71 TCs S size = 110 man/h</p><p>140 TCs M Size = 520 man/h</p><p>
        7 TCs L Size = 40 man/h</p><p><br /></p><p>Since it is important to start with Critical or Major test cases and skip Minor
        ones the estimation will be:</p><p>110 Major:<br /> - 20 of them S Size = 20h</p><p> - 75 of them M Size = 225h</p><p> - 
        5 of them L Size = 25h</p><p><br /></p><p>Critical already should be covered with automation tests.</p>","representation":
        "storage","_expandable":{"content":"/rest/api/content/2408012834"}},"_expandable":{"editor":"","view":"","export_view":"",
        "styled_view":"","anonymous_export_view":""}},"extensions":{"position":"none"},"_links":{"webui":"/display/EPMCDME/
        AQA+Backlog+Estimation","edit":"/pages/resumedraft.action?draftId=2408012834&draftShareId=64d72453-1668-4cfe-b2cb-2657f2bf2d74"
        ,"tinyui":"/x/IlyHjw","self":"https://kb.epam.com/rest/api/content/2408012834"},"_expandable":{"container":"/rest/api/space/EPMCDME"
        ,"metadata":"","operations":"","children":"/rest/api/content/2408012834/child","restrictions":"/rest/api/content/2408012834/
        restriction/byOperation","history":"/rest/api/content/2408012834/history","ancestors":"","version":"","descendants":"/rest/
        api/content/2408012834/descendant","space":"/rest/api/space/EPMCDME"}}],"start":0,"limit":5,"size":1,"cqlQuery":"title ~ "AQA
        backlog estimation"","searchDuration":1359,"totalSize":1,"_links":{"self":"https://kb.epam.com/rest/api/content/search?
        expand=body.storage&cql=title+~+%22AQA+backlog+estimation%22","base":"https://kb.epam.com","context":""}}
        """,
    ),
]

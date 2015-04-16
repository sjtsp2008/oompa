#
# GitHubNeo.py
#
# note: i tried using bulbs, which would be easier to
#       migrate to other tinkerpop graph engines, but had
#       trouble authenticating
#

from oompa.tracking.github               import github_utils

import py2neo

from py2neo import Graph, Node, Relationship



"""


visit: http://localhost:7474/

  default user - neo4j


part of neo walkthrough


  CREATE (ee:Person { name: "Emil", from: "Sweden", klout: 99 })

    () means "node"
    {} surround attrs
    Person is the label
    

  MATCH (ee:Person) WHERE ee.name = "Emil" RETURN ee;

complex creation:

MATCH (ee:Person) WHERE ee.name = "Emil"
CREATE (js:Person { name: "Johan", from: "Sweden", learn: "surfing" }),
(ir:Person { name: "Ian", from: "England", title: "author" }),
(rvb:Person { name: "Rik", from: "Belgium", pet: "Orval" }),
(ally:Person { name: "Allison", from: "California", hobby: "surfing" }),
(ee)-[:KNOWS {since: 2001}]->(js),(ee)-[:KNOWS {rating: 5}]->(ir),
(js)-[:KNOWS]->(ir),(js)-[:KNOWS]->(rvb),
(ir)-[:KNOWS]->(js),(ir)-[:KNOWS]->(ally),
(rvb)-[:KNOWS]->(ally)

pattern matching:

MATCH (ee:Person)-[:KNOWS]-(friends)
WHERE ee.name = "Emil" RETURN ee, friends





Pattern matching can be used to make recommendations. Johan is
learning to surf, so he may want to find a new friend who already
does:

  MATCH (js:Person)-[:KNOWS]-()-[:KNOWS]-(surfer)
  WHERE js.name = "Johan" AND surfer.hobby = "surfing"
  RETURN DISTINCT surfer

    ()        empty parenthesis to ignore these nodes
    DISTINCT  because more than one path will match the pattern
    surfer    will contain Allison, a friend of a friend who surfs


"""


class GitHubNeo:
    """
    interface for lazy github graph in neo4j

      - update
      - list
      - track
      - discover

    """
    
    def __init__(self, config, githubHelper):

        # XXX get from config
        neo_url    = "http://localhost:7474/db/data/"
        neo_host   = "localhost:7474"
        neo_user   = "neo4j"
        neo_passwd = "neotest"
        
        py2neo.authenticate(neo_host, neo_user, neo_passwd)

        self.graph        = py2neo.Graph(neo_url)

        self.githubHelper = githubHelper
        
        return


    def updateRelationshipsTo(self, obj, slot, relationshipLabel, destNode):
        """
        TODO: support attribute decorators
        """
        
        graph = self.graph

        # XXX need to determine nodeType by slot name
        # TODO: use a dictionary - simpler

        if slot == "stargazers":
            nodeType = "User"
        else:
            xxx
            pass
        
        for value in getattr(obj, slot)():

            # value is another github object (User, ...)
            
            # name    = value.name
            name    = str(value)
            
            print("  %s: %s" % ( relationshipLabel, name ))

            srcNode = Node(nodeType, name = name)
            graph.create(Relationship(srcNode, relationshipLabel, destNode))
            pass

        # need to flush anything?
        
        return

        
    
    def updateRepo(self, name, repo):
        """
        repo is a GitHub3 Repository
        """

        graph = self.graph
        
        # was it forked from something?
        print("GitHubNeo.updateRepo(): %s" % repo.full_name)

        # TODO: i think bulb seems to have better object modeling
        
        # what if it already exists?
        repoNode = Node("Repository",   name = repo.full_name)


        # TODO: only if it does not exist
        graph.create(repoNode)

        # XXX need a general map of method/list-name to relationship label
        relationship = "STARRED"

        # TODO: cache user nodes - may also be on contributes, subscribes

        self.updateRelationshipsTo(repo, "stargazers", "STARRED", repoNode)
        
        return

        # TODO: capture all of this metadata, ...
    
        print("  parent:          %s" % obj.parent)
        print("  source:          %s" % obj.source)
        print("  description:     %s" % obj.description.encode("utf8"))
        print("  homepage:        %s" % obj.homepage)
        print("  language:        %s" % obj.language)
        print("  last_modified:   %s" % obj.last_modified)
        print("  updated_at:      %s" % obj.updated_at)
        
        # branches()
        
        # code_frequency()
        
        # XXX blocked - requires authentication
        # dumpList(obj, "collaborators")
        
        # comments()
        
        # commit_activity()
        # commits()
        
        # contributor_statistics()
        
        github_utils.dumpList(obj, "contributors")
        
        # default_branch
        
        # deployments() ???
        
        # events()
        
        github_utils.dumpList(obj, "forks")
        
        # hooks() ???
        
        # issues()
        
        # keys() ???
        
        # labels() ???   i think these are tags used in issues/planning
        
        github_utils.dumpList(obj, "languages")
        
        # milestones()
        
        # notifications()
        
        # open_issues_count ???
        
        # owner  (a User object)
        
        # pull_requests
        
        # refs() ???
        
        # releases() ???
        
        # size (what are units?)
        
        # statuses() ?
        
        github_utils.dumpList(obj, "subscribers")
        
        # tags()
        
        # i think that tree is some sort of file tree.  (i was hoping it was fork ancestry)
        # tree = obj.tree()
        # print("TREE: %s" % tree)
        
        # teams()
        
        # { "Last-Modified": "", "all": [0, 0, 1, 1, ..., (52 weeks?) ], "owner": [ 0, 0, 0, 0, ... ] }
        print("  weekly_commit_count:   %s" % obj.weekly_commit_count())

        return
        

    
    def update(self, args):
        """
        args is list of strings - can be repo (with a slash), org, or user.
        
        helper attempts to determine the kind

        """
        
        print("update: %s" % ( args, ))
        
        for kind, name, obj in self.githubHelper.getKindNameAndObject(args):

            print("%s: %s - %s" % ( kind, name, obj.name ))

            # common across User and Organization
            print("  url:          %s" % obj.html_url)

            if kind == "user":

                xxx
                user = obj

                print("  bio:      %s" % obj.bio)
                print("  company:  %s" % obj.company)
                print("  location: %s" % obj.location)
                print("  blog:     %s" % user.blog)
                print("  plan:     %r" % user.plan)
                
                dumpList(obj, "followers")
                dumpList(obj, "following")
                dumpList(obj, "organizations")
                dumpList(obj, "starred_repositories")
                dumpList(obj, "subscriptions")
                
                # XXX why is this access different?
                for repository in github3.repositories_by(user.login):
                    print("  repo:           %s" % repository)
                    pass
                pass

            elif kind == "org":

                xxx
                
                print("  bio:      %s" % obj.bio)
                print("  company:  %s" % obj.company)
                print("  location: %s" % obj.location)

                dumpList(obj, "public_members")
                dumpList(obj, "repositories")
            
            elif kind == "repo":

                self.updateRepo(name, obj)
                
            else:
                xxx
                pass

            print("")
            pass

        return

    pass


    

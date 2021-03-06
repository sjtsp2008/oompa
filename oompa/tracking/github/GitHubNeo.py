#
# GitHubNeo.py
#
# note: i tried using bulbs, which would be easier to
#       migrate to other tinkerpop graph engines, but had
#       trouble authenticating
#
#

"""
package oompa.tracking.github

experiments with working on github graphs in neo

uses py2neo

TODO: i think bulb seems to have better object modeling (but doesn't work for me)

"""

from datetime import timedelta
from datetime import datetime

import py2neo

from oompa.tracking.github import github_utils


Node         = py2neo.Node
Relationship = py2neo.Relationship



"""
misc neo notes:

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


def parseFreshness(freshness):
    """
    TODO: not fully general/bulletproof yet
    """

    pieces = freshness.split()

    days    = 0
    hours   = 0
    minutes = 0

    for piece in pieces:
        unit  = piece[-1]
        value = int(piece[:-1])

        if unit == "d":
            days = value
        elif unit == "h":
            hours = value
        elif unit == "m":
            minutes = value
        else:
            raise Exception("unknown time unit", unit, freshness)
        pass

    freshness_delta = timedelta(days = days, hours = hours, minutes = minutes)

    return freshness_delta


class GitHubNeo:
    """
    interface for lazy github graph in neo4j

      - update
      - list
      - track
      - discover

    """

    # ISO format
    _dtFormat = "%Y-%m-%dT%H:%M:%S"

    def __init__(self, config, githubHelper):

        # XXX get from config
        neo_url    = config.get("neo.github.url")
        neo_user   = config.get("neo.github.user")
        neo_passwd = config.get("neo.github.passwd")

        # TODO: derive from the url
        neo_host   = "localhost:7474"

        # TODO: if freshness, parse it to a real latency (e.g., "4d" -> seconds)

        self.freshness = config.get("neo.github.freshness")

        if self.freshness:
            self.freshness = parseFreshness(self.freshness)
            pass

        py2neo.authenticate(neo_host, neo_user, neo_passwd)

        self.graph        = py2neo.Graph(neo_url)
        self.githubHelper = githubHelper

        self._establishNeoSchema()

        return



    def _establishNeoSchema(self):
        """
        set up constraints on relationships and nodes in neo graph

        note: i believe that schema constraints are volatile, per-session

            if i don't apply these contraints, on a graph that had them
            in previous sessions, i can violate the previous contraints
        """

        schema = self.graph.schema

        try:
            schema.create_uniqueness_constraint("User",         "name")
            schema.create_uniqueness_constraint("Organization", "name")
            schema.create_uniqueness_constraint("Repository",   "name")
        # except py2neo.error.ConstraintViolationException:
        except:
            # already established
            return

        # TODO: User
        # TODO: Organization
        # TODO: relationships

        return


    def query(self, query):
        """
        submit arbitrary cypher-syntax query to graph

        query is a string

        """

        for record in self.graph.cypher.execute(query):
            yield record

        return


    def getNodeType(self, node):
        """
        return the type of the given node
        """
        
        # XXX still figuring out LabelSet - don't know how to get values as list
        return node.labels.copy().pop()

    
    def getNode(self, nodeName, nodeType = None):
        """

        returns a neo Node

        TODO: if nodeType specified, use it (esp User vs Organization)
        """

        # print("NT: %s" % nodeType)
        
        typeSpec = ""

        # XXX figure out best way to support this
        # if nodeType is not None:
        #    typeSpec = ":%s" % nodeType
        #    pass

        # XXX this does not feel like "The Best Way" to simply get a node
        query   = 'MATCH (node {name:"%s"}%s) RETURN node' % ( nodeName, typeSpec )

        # print("  Q: %r" % query)
        
        records = list(self.query(query))

        if not records:
            return None

        if len(records) > 1:
            print("XXX getNode() plural records: %s %s (%r)" % ( nodeType, nodeType, typeSpec ))
            for record in records:
                print("  R: %r" % ( record, ))
                pass
            xxx
            pass
        
        record = records[0]

        return self.graph.hydrate(record[0])


    def _now(self):

        return datetime.utcnow().replace(microsecond = 0)

    def _parseISODTStr(self, dtStr):

        return datetime.strptime(dtStr, self._dtFormat)
    

    

    def createNode(self, name, nodeType):

        # we don't want the microsecond junk in time string
        now   = self._now()

        node  = Node(nodeType, name = name, createdDT = now.isoformat())

        self.graph.create(node)

        return node

    
    
    def getOrAddNode(self, name, nodeType = None):

        node = self.getNode(name, nodeType)

        if node is not None:
            # print("# node already in graph")
            return node

        # print("# node not in graph - have to create")
        
        if nodeType is None:
            for nodeType, name, obj in self.githubHelper.getKindNameAndObject([ name, ]):
                # only one
                break

            if nodeType is None:
                print("  could not determine nodeType for name: %s" % name)
                xxx
                pass
            pass

        return self.createNode(name, nodeType)



    

    #
    # neo edge relationships for lists "away from" certain types of github objects
    #
    # some list names have an alias, because the list name is confusing
    #
    # TODO: test if simple rule of removing the final "s" works.  that would be simpler
    #   - there are a couple of exceptions
    #
    _relationships = {

        "Repository" : [

            ( "stargazers",    "starred",     "from", ),

            ( "subscribers",   "subscriber",  "from", ),
            ( "contributors",  "contributor", "from", ),

            ( "forks",         "forkOf",      "from", ),
            # ...
        ],

        "User" : [
            ( "followers",            "follows",   "from", ),
            ( "following",            "follows",    "to",  ),
            ( "starred_repositories", "starred",    "to",  ),
            ( "subscriptions",        "subscriber", "to",  ),
            ( "organizations",        "memberOf",   "to",  ),
        ],
    }

    
    def updateRelationships(self, obj, slot, relationshipLabel, direction, destNode):
        """

        obj is a github3 object (repository, user, organization)

        direction is "from" or "to"

        TODO: support attribute decorators

        generates stream of entitySpec

        """

        destNodeType = self.getNodeType(destNode)
        graph        = self.graph

        print("updateRelationships: %-25s - %-25s %4s - %s" % (
            slot, relationshipLabel, direction, destNode.properties["name"] ))

        # XXX need otherNodeLabelGetter
        #   - .name, .login, ...

        # determine neighbor nodeType by slot name
        # TODO: use a dictionary - simpler

        neighborNodeType = None
        
        # XXX just figure this out by what we get back
        if slot in [ "stargazers", "contributors", ]:
            neighborNodeType = "User"
        elif slot in [ "followers", "following" ]:
            neighborNodeType = "User"
        elif slot == "organizations":
            neighborNodeType = "Organization"
        elif slot == "starred_repositories":
            neighborNodeType = "Repository"
        elif slot == "subscriptions":
            neighborNodeType = "Repository"
        elif slot == "forks":
            neighborNodeType = "Repository"
        elif slot == "subscribers":
            # i think that things can subsribe to users or orgs, too
            # this is currently just Users subscribed to Repository
            neighborNodeType = "User"
        else:
            print("  XXX slot not handled in switch yet - %r" % slot)
            xxx
            pass

        if neighborNodeType == "User":
            nodeNameAttr = "login"
        elif neighborNodeType == "Organization":
            nodeNameAttr = "name"
        elif neighborNodeType == "Repository":
            nodeNameAttr = "full_name"
        else:
            xxx
            pass

        # print("# nodeNameAttr: %s - %s - %s" % ( slot, neighborNodeType, nodeNameAttr ))

        # TODO: get all of them, and batch-update

        neighbors = []
        
        for value in getattr(obj, slot)():

            # if slot == "forks":
            #    print("  fork obj")
            #    github_utils.dumpSlotValues(obj)
            
            # value is another github object (User, ...)
            
            # name    = value.name
            # name    = str(value)
            nodeName = getattr(value, nodeNameAttr)

            neighbors.append(( neighborNodeType, nodeName ))
            pass

        # TODO: batch-update

        neighbors = sorted(neighbors, key = lambda _tuple : _tuple[1])
        
        for neighborNodeType, nodeName in neighbors:

            # only if verbose tracing
            # print("  %s: %r" % ( relationshipLabel, nodeName ))

            srcNode = Node(neighborNodeType, name = nodeName)

            # graph.merge_one(Relationship(srcNode, relationshipLabel, destNode))
            # XXX try/except is sloppy - i don't get merge vs create yet

            if direction == "from":
                relationship = Relationship(srcNode, relationshipLabel, destNode)
            else:
                relationship = Relationship(destNode, relationshipLabel, srcNode)
                pass

            try:
                graph.create(relationship)
            except:
                # already exists
                pass

            yield ( neighborNodeType, nodeName )
            pass

        # need to flush anything?
        
        return


    def _getRelationshipTuples(self, nodeType, relationships = None):
        """
        TODO: memoize
        """

        # print("_getRelationshipTuples(): %s %s" % ( nodeType, relationships ))
        
        #
        # XXX still working out the best way to normalize github
        #     relationships to neo relationships
        #

        for relationshipTuple in self._relationships[nodeType]:

            listName, relationshipLabel, direction = relationshipTuple

            if relationships:

                keep = False

                for rel in relationships:
                    if rel == relationshipLabel:
                        keep = True
                        break
                    pass

                if not keep:
                    continue
                pass

            yield relationshipTuple
            pass

        return

    
    def updateGithubObj(self, githubObj, node, relationships = None):
        """
        githubObj is a GitHub3 Repository, User, or Organization
        node is a py2neo Node
        """

        # starting to generalize

        graph    = self.graph
        nodeType = self.getNodeType(node)

        # note that full_name is something that i attach
        if nodeType == "Repository":
            name = githubObj.full_name
        else:
            name = githubObj.name
            pass

        # TODO: want to report different things for different object -
        #       user needs login and name

        print("GitHubNeo.updateGithubObj(): %s" % name.encode("utf8"))

        relationshipTuples = list(self._getRelationshipTuples(nodeType, relationships))

        # TODO: *local* LRU cache user and repo - may also be on contributes, subscribes.
        #       make sure we only pay github points once

        for listName, relationshipLabel, direction in relationshipTuples:
            for entitySpec in self.updateRelationships(githubObj,
                                                       listName,
                                                       relationshipLabel,
                                                       direction,
                                                       node):
                yield entitySpec
                pass
            pass

        node.properties["updatedDT"] = datetime.utcnow().replace(microsecond = 0)
        node.push()

        # what else should go in graph?
        #  .parent
        #  .source
        #  .description
        #  .homepage
        #  .language
        #  .last_modified
        #  .updated_at

        # branches()
        
        # code_frequency()
        
        # XXX blocked - requires authentication
        # dumpList(obj, "collaborators")
        
        # comments()
        
        # commit_activity()
        # commits()
        
        # contributor_statistics()
        
        # github_utils.dumpList(obj, "contributors")
        
        # default_branch
        
        # deployments() ???
        
        # events()
        
        # github_utils.dumpList(obj, "forks")
        
        # hooks() ???
        
        # issues()
        
        # keys() ???
        
        # labels() ???   i think these are tags used in issues/planning
        
        # github_utils.dumpList(obj, "languages")

        # milestones()

        # notifications()
        
        # open_issues_count ???
        
        # owner  (a User object)
        
        # pull_requests
        
        # refs() ???
        
        # releases() ???
        
        # size (what are units?)
        
        # statuses() ?
        
        # github_utils.dumpList(obj, "subscribers")
        
        # tags()
        
        # i think that tree is some sort of file tree.  (i was hoping it was fork ancestry)
        # tree = obj.tree()
        # print("TREE: %s" % tree)
        
        # teams()
        
        # { "Last-Modified": "",
        #   "all": [0, 0, 1, 1, ..., (52 weeks?) ],
        #   "owner": [ 0, 0, 0, 0, ... ] }
        # print("  weekly_commit_count:   %s" % obj.weekly_commit_count())

        return


    def updateUser(self, githubObj, node):
        """
        user is a GitHub3 User

        TODO: refactor - merge with updateRepository - just a generic 
        """

        graph    = self.graph
        nodeType = self.getNodeType(node)
                
        # was it forked from something?
        print("GitHubNeo.updateUser(): %s - %r" % ( user.login, user.name ))

        nodeType = "User"
        node     = Node(nodeType, name = user.login)

        # use merge_one to create if it does not already exist
        # XXX merge_one does not persist the node?
        # graph.merge_one(node)
        graph.create(node)

        for listNameTuple in self._relationships[nodeType]:
            if isinstance(listNameTuple, tuple):
                listNameTuple, relationshipLabel = listNameTuple
            else:
                listName          = listNameTuple
                relationshipLabel = listName
                pass
            
            for entitySpec in self.updateRelationships(user, listName, relationshipLabel, node):
                yield entitySpec
                pass
            pass
        
        return


    def updateOrganization(self, name, org):
        """
        org is a GitHub3 Organization
        """

        graph = self.graph

        # was it forked from something?
        print("GitHubNeo.updateOrg(): %s" % user)

        xxx
                
        print("  bio:      %s" % obj.bio)
        print("  company:  %s" % obj.company)
        print("  location: %s" % obj.location)
        
        dumpList(obj, "public_members")
        dumpList(obj, "repositories")

        return



    def _nodeFreshEnough(self, node):

        updatedDTStr = node.properties.get("updatedDT")

        if updatedDTStr:

            age = self._now() - self._parseISODTStr(updatedDTStr)

            if age <= self.freshness:
                return True
            pass

        return False


    def _getCachedNeighbors(self, node, relationships = None):

        nodeType = self.getNodeType(node)

        # print("  _getCachedNeighbors(): %-12s %s" % ( nodeType, node.properties["name"] ))

        if relationships is None:
            #
            # list of ( githubSlot, neoRelationLabel )
            #
            relationships    = self._relationships[nodeType]
                  
            neoRelationships = []

            for relationshipInfo in relationships:
                if isinstance(relationshipInfo, tuple):
                    neoRelationship = relationshipInfo[1]
                else:
                    neoRelationship = relationshipInfo
                    pass
                neoRelationships.append(neoRelationship)
                pass
            pass
        else:
            #
            # map relationships in to neo relationships
            #
            neoRelationships = relationships
            pass

        i = 1
        
        for neoRelationship in neoRelationships:

            # print("  neoRelationship: %s" % neoRelationship)

            neighbors = []
            
            for rel in node.match(neoRelationship):

                if node == rel.start_node:
                    neighborNode = rel.end_node
                else:
                    neighborNode = rel.start_node
                    pass
                
                # XXX expensive.  we can already know this, from the neoRelationship
                neighborNodeType = self.getNodeType(neighborNode)

                # yield neighborNodeType, neighborNode.properties["name"]
                neighbors.append(( neighborNodeType, neighborNode.properties["name"], 1 ))

                i += 1
                pass

            if neighbors:
                print("    %5d  %s" % ( len(neighbors), neoRelationship ))
                pass

            # XXX optional.  user may want to sort by something else
            #     (added date - but that's not supported yet)

            neighbors = sorted(neighbors, key = lambda _tuple : _tuple[1])
            
            for neighborTuple in neighbors:
                yield neighborTuple
                pass
            
            pass
        
        return

    
    def update(self, entitySpecs, numHops = None, relationships = None):
        """update the edges/relationships around the specified node names

        creates the nodes if they don't already exist

        entitySpecs is list of github names - Repository, User,
        Organization.  can by type-hinted - org:..., user:...,
        repo:..., or else we guess, using the helper

        if staleness constraints specified, will use what's in cache
        if new enough (to save github points)

        TODO: maybe able to specify only certain relationship types to update
        """

        if numHops is None:
            numHops = 1
            pass

        hop      = 1

        # list of entities left to check, and their hop
        #
        # a seed is at hop 1 (versus 0)
        boundary = []

        for entitySpec in entitySpecs:
            boundary.append(( entitySpec, hop ))
            pass

        helper    = self.githubHelper
        freshness = self.freshness
        
        while boundary:
                
            entitySpec, _hop = boundary[0]
            boundary         = boundary[1:]

            print("GitHubNeo.update: %s  %5d  %5d  %s" %
                  ( _hop, len(boundary), helper.checkRatePointsLeft(), entitySpec, ))

            nodeType = None
            extra    = None

            if isinstance(entitySpec, tuple):
                nodeType = entitySpec[0]
                name     = entitySpec[1]

                if len(entitySpec) > 2:
                    extra = entitySpec[2]
                    pass
                pass
            else:
                name     = entitySpec
                pass

            node      = self.getOrAddNode(name, nodeType)
            nodeType  = self.getNodeType(node)
            
            if freshness is not None and self._nodeFreshEnough(node):
                # print("  using cached relationships: %s - %s" % ( nodeType, name ))
                neighbors = self._getCachedNeighbors(node, relationships = relationships)
            else:
                githubObj = helper.getGithubObject(name, nodeType)
                neighbors = self.updateGithubObj(githubObj, node, relationships = relationships)
                pass
                
            # need to drain the stream, even if we don't add them to boundary
            neighbors = list(neighbors)
            
            if _hop < numHops:
                for _entitySpec in neighbors:
                    boundary.append(( _entitySpec, _hop + 1 ))
                    # print("  added to boundary: %s %s" % ( _hop + 1, _entitySpec ))
                    pass
                pass
            # print("")
            pass
        
        return

    pass


    

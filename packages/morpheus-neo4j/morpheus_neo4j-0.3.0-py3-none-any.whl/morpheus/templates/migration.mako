"""
${name.replace("_", " ").title()}

Migration ID: ${migration_id}
Created: ${created_time}
"""

from morpheus.models.migration import MigrationBase
from morpheus.models.priority import Priority


class ${"".join(word.capitalize() for word in name.split("_") if not word.isdigit())}(MigrationBase):
    """${name.replace("_", " ").title()} migration."""
    
    # DAG Dependencies - migrations this one depends on
    dependencies = [
% for dep in dependencies:
        "${dep}",
% endfor
    ]
    
    # Conflicts - migrations that cannot run in parallel with this one
    conflicts = [
% for conflict in conflicts:
        "${conflict}",
% endfor
    ]
    
    # Tags for filtering/grouping
    tags = [
% for tag in tags:
        "${tag}",
% endfor
    ]
    
    # Priority (higher priority runs first when parallel)
    priority = Priority.${priority.name if hasattr(priority, 'name') else 'NORMAL'}
    
    def upgrade(self, tx) -> None:
        """
        Upgrade database schema.
        
        Args:
            tx: Neo4j transaction instance for executing queries
        """
        # Add your upgrade queries here
% if template_type == "constraint":
        # Example constraints:
        # tx.run("CREATE CONSTRAINT user_email IF NOT EXISTS FOR (u:User) REQUIRE u.email IS UNIQUE")
        # tx.run("CREATE CONSTRAINT post_id IF NOT EXISTS FOR (p:Post) REQUIRE p.id IS UNIQUE")
% elif template_type == "index":
        # Example indexes:
        # tx.run("CREATE INDEX user_name IF NOT EXISTS FOR (u:User) ON (u.name)")
        # tx.run("CREATE INDEX post_created IF NOT EXISTS FOR (p:Post) ON (p.created_at)")
% elif template_type == "relationship":
        # Example relationships:
        # tx.run("MATCH (u:User {id: $user_id}), (p:Post {id: $post_id}) CREATE (u)-[:LIKES]->(p)", user_id=123, post_id=456)
        # tx.run("MATCH (u1:User {id: $follower_id}), (u2:User {id: $followed_id}) CREATE (u1)-[:FOLLOWS]->(u2)", follower_id=123, followed_id=456)
% elif template_type == "data":
        # Example data migrations with conditional logic:
        # result = tx.run("MATCH (u:User) RETURN count(u) as user_count")
        # user_count = result.single()["user_count"]
        # if user_count > 1000:
        #     tx.run("MATCH (u:User) WHERE u.legacy_field IS NOT NULL SET u.new_field = u.legacy_field")
        # else:
        #     tx.run("MATCH (u:User) SET u.migrated_at = datetime()")
% else:
        # Example queries:
        # tx.run("CREATE CONSTRAINT user_email IF NOT EXISTS FOR (u:User) REQUIRE u.email IS UNIQUE")
        # tx.run("CREATE INDEX user_name IF NOT EXISTS FOR (u:User) ON (u.name)")
% endif
        pass
    
    def downgrade(self, tx) -> None:
        """
        Downgrade database schema.
        
        Args:
            tx: Neo4j transaction instance for executing queries
        """
        # Add your downgrade queries here (reverse of upgrade)
% if template_type == "constraint":
        # Example constraint removal:
        # tx.run("DROP CONSTRAINT user_email IF EXISTS")
        # tx.run("DROP CONSTRAINT post_id IF EXISTS")
% elif template_type == "index":
        # Example index removal:
        # tx.run("DROP INDEX user_name IF EXISTS")
        # tx.run("DROP INDEX post_created IF EXISTS")
% elif template_type == "relationship":
        # Example relationship removal:
        # tx.run("MATCH (u:User)-[r:LIKES]->(p:Post) WHERE u.id = $user_id AND p.id = $post_id DELETE r", user_id=123, post_id=456)
        # tx.run("MATCH (u1:User)-[r:FOLLOWS]->(u2:User) WHERE u1.id = $follower_id AND u2.id = $followed_id DELETE r", follower_id=123, followed_id=456)
% elif template_type == "data":
        # Example data rollback:
        # tx.run("MATCH (u:User) WHERE u.new_field IS NOT NULL REMOVE u.new_field")
        # tx.run("MATCH (n) WHERE n.migrated_at IS NOT NULL REMOVE n.migrated_at")
% else:
        # Example rollback queries:
        # tx.run("DROP CONSTRAINT user_email IF EXISTS")
        # tx.run("DROP INDEX user_name IF EXISTS")
% endif
        pass
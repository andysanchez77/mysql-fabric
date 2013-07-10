import unittest
import uuid as _uuid
import mysql.fabric.sharding as _sharding
import mysql.fabric.errors as _errors
import tests.utils

from mysql.fabric.sharding import ShardMapping, HashShardingSpecification, Shards
from mysql.fabric.server import Group, MySQLServer
from mysql.fabric import persistence

from tests.utils import ShardingUtils, MySQLInstances

class TestHashSharding(unittest.TestCase):
    def setUp(self):
        self.__options_1 = {
            "uuid" :  _uuid.UUID("{aa75b12b-98d1-414c-96af-9e9d4b179678}"),
            "address"  : MySQLInstances().get_address(0),
            "user" : "root"
        }

        uuid_server1 = MySQLServer.discover_uuid(**self.__options_1)
        self.__options_1["uuid"] = _uuid.UUID(uuid_server1)
        self.__server_1 = MySQLServer(**self.__options_1)
        MySQLServer.add(self.__server_1)

        self.__group_1 = Group("GROUPID1", "First description.")
        Group.add(self.__group_1)
        self.__group_1.add_server(self.__server_1)
        self.__group_1.master = self.__options_1["uuid"]

        self.__options_2 = {
            "uuid" :  _uuid.UUID("{aa45b12b-98d1-414c-96af-9e9d4b179678}"),
            "address"  : MySQLInstances().get_address(1),
            "user" : "root"
        }

        uuid_server2 = MySQLServer.discover_uuid(**self.__options_2)
        self.__options_2["uuid"] = _uuid.UUID(uuid_server2)
        self.__server_2 = MySQLServer(**self.__options_2)
        MySQLServer.add(self.__server_2)

        self.__group_2 = Group("GROUPID2", "Second description.")
        Group.add(self.__group_2)
        self.__group_2.add_server(self.__server_2)
        self.__group_2.master = self.__options_2["uuid"]

        self.__options_3 = {
            "uuid" :  _uuid.UUID("{bb75b12b-98d1-414c-96af-9e9d4b179678}"),
            "address"  : MySQLInstances().get_address(2),
            "user" : "root"
        }

        uuid_server3 = MySQLServer.discover_uuid(**self.__options_3)
        self.__options_3["uuid"] = _uuid.UUID(uuid_server3)
        self.__server_3 = MySQLServer(**self.__options_3)
        MySQLServer.add( self.__server_3)

        self.__group_3 = Group("GROUPID3", "Third description.")
        Group.add( self.__group_3)
        self.__group_3.add_server(self.__server_3)
        self.__group_3.master = self.__options_3["uuid"]

        self.__options_4 = {
            "uuid" :  _uuid.UUID("{bb45b12b-98d1-414c-96af-9e9d4b179678}"),
            "address"  : MySQLInstances().get_address(3),
            "user" : "root"
        }

        uuid_server4 = MySQLServer.discover_uuid(**self.__options_4)
        self.__options_4["uuid"] = _uuid.UUID(uuid_server4)
        self.__server_4 = MySQLServer(**self.__options_4)
        MySQLServer.add(self.__server_4)

        self.__group_4 = Group("GROUPID4", "Fourth description.")
        Group.add( self.__group_4)
        self.__group_4.add_server(self.__server_4)
        self.__group_4.master = self.__options_4["uuid"]

        self.__options_5 = {
            "uuid" :  _uuid.UUID("{cc75b12b-98d1-414c-96af-9e9d4b179678}"),
            "address"  : MySQLInstances().get_address(4),
            "user" : "root"
        }

        uuid_server5 = MySQLServer.discover_uuid(**self.__options_5)
        self.__options_5["uuid"] = _uuid.UUID(uuid_server5)
        self.__server_5 = MySQLServer(**self.__options_5)
        MySQLServer.add(self.__server_5)

        self.__group_5 = Group("GROUPID5", "Fifth description.")
        Group.add( self.__group_5)
        self.__group_5.add_server(self.__server_5)
        self.__group_5.master = self.__options_5["uuid"]

        self.__options_6 = {
            "uuid" :  _uuid.UUID("{cc45b12b-98d1-414c-96af-9e9d4b179678}"),
            "address"  : MySQLInstances().get_address(5),
            "user" : "root"
        }

        uuid_server6 = MySQLServer.discover_uuid(**self.__options_6)
        self.__options_6["uuid"] = _uuid.UUID(uuid_server6)
        self.__server_6 = MySQLServer(**self.__options_6)
        MySQLServer.add(self.__server_6)

        self.__group_6 = Group("GROUPID6", "Sixth description.")
        Group.add( self.__group_6)
        self.__group_6.add_server(self.__server_6)
        self.__group_6.master = self.__options_6["uuid"]

        self.__shard_mapping_list = ShardMapping.list_shard_mapping_defn()
        self.assertEquals( self.__shard_mapping_list,  [])

        self.__shard_mapping_id_1 = ShardMapping.define("HASH", "GROUPID1")

        self.__shard_mapping_1 = ShardMapping.add(self.__shard_mapping_id_1, "db1.t1", "userID1")

        self.__shard_1 = Shards.add("GROUPID2")
        self.__shard_2 = Shards.add("GROUPID3")
        self.__shard_3 = Shards.add("GROUPID4")
        self.__shard_4 = Shards.add("GROUPID5")
        self.__shard_5 = Shards.add("GROUPID6")

        self.__hash_sharding_specification_1 = HashShardingSpecification.add(
            self.__shard_mapping_1.shard_mapping_id,
            self.__shard_1.shard_id
        )

        self.__hash_sharding_specification_2 = HashShardingSpecification.add(
            self.__shard_mapping_1.shard_mapping_id,
            self.__shard_2.shard_id
        )

        self.__hash_sharding_specification_3 = HashShardingSpecification.add(
            self.__shard_mapping_1.shard_mapping_id,
            self.__shard_3.shard_id
        )

        self.__hash_sharding_specification_4 = HashShardingSpecification.add(
            self.__shard_mapping_1.shard_mapping_id,
            self.__shard_4.shard_id
        )

        self.__hash_sharding_specification_5 = HashShardingSpecification.add(
            self.__shard_mapping_1.shard_mapping_id,
            self.__shard_5.shard_id
        )

    def test_hash_lookup(self):
        """Test the hash sharding lookup.
        """
        shard_1_cnt = 0
        shard_2_cnt = 0
        shard_3_cnt = 0
        shard_4_cnt = 0
        shard_5_cnt = 0

        #Lookup a range of keys to ensure that both the shards are
        #utilized.
        for i in range(0,  1000):
            hash_sharding_spec_1 = HashShardingSpecification.lookup(
                                        i,
                                        self.__shard_mapping_id_1
                                    )
            if self.__shard_1.shard_id == hash_sharding_spec_1.shard_id:
                shard_1_cnt = shard_1_cnt + 1
            elif self.__shard_2.shard_id == hash_sharding_spec_1.shard_id:
                shard_2_cnt = shard_2_cnt + 1
            elif self.__shard_3.shard_id == hash_sharding_spec_1.shard_id:
                shard_3_cnt = shard_3_cnt + 1
            elif self.__shard_4.shard_id == hash_sharding_spec_1.shard_id:
                shard_4_cnt = shard_4_cnt + 1
            elif self.__shard_5.shard_id == hash_sharding_spec_1.shard_id:
                shard_5_cnt = shard_5_cnt + 1

        #The following will ensure that both the hash shards are utilized
        #to store the keys and the values are not skewed in one shard.
        self.assertTrue(shard_1_cnt > 0)
        self.assertTrue(shard_2_cnt > 0)
        self.assertTrue(shard_3_cnt > 0)
        self.assertTrue(shard_4_cnt > 0)
        self.assertTrue(shard_5_cnt > 0)

    def test_hash_remove(self):
        """Test the removal of hash shards.
        """
        hash_sharding_specification_1 = HashShardingSpecification.fetch(1)
        hash_sharding_specification_2 = HashShardingSpecification.fetch(2)
        hash_sharding_specification_3 = HashShardingSpecification.fetch(3)
        hash_sharding_specification_4 = HashShardingSpecification.fetch(4)
        hash_sharding_specification_5 = HashShardingSpecification.fetch(5)
        hash_sharding_specification_1.remove()
        hash_sharding_specification_2.remove()
        hash_sharding_specification_3.remove()
        hash_sharding_specification_4.remove()
        hash_sharding_specification_5.remove()

        self.__shard_1.remove()
        self.__shard_2.remove()
        self.__shard_3.remove()
        self.__shard_4.remove()
        self.__shard_5.remove()

        for i in range(0,  10):
            hash_sharding_spec = HashShardingSpecification.lookup(
                                        i,
                                        self.__shard_mapping_id_1
                                    )
            self.assertEqual(hash_sharding_spec,  None)

    def test_list_shard_mapping(self):
        """Test the listing of HASH shards in a shard mapping.
        """
        expected_shard_mapping_list1 =   [1, "HASH", "GROUPID1"]
        obtained_shard_mapping_list = ShardMapping.list_shard_mapping_defn()
        self.assertEqual(set(expected_shard_mapping_list1),
                         set(obtained_shard_mapping_list[0]))

    def test_shard_mapping_list_mappings(self):
        """Test the listing of all HASH shards in a shard mapping.
        """
        shard_mappings = ShardMapping.list("HASH")
        self.assertTrue(ShardingUtils.compare_shard_mapping
                         (self.__shard_mapping_1, shard_mappings[0]))

    def test_fetch_sharding_scheme(self):
        """Test the fetch method of the HASH sharding scheme.
        """
        hash_sharding_specification_1 = HashShardingSpecification.fetch(1)
        hash_sharding_specification_2 = HashShardingSpecification.fetch(2)
        hash_sharding_specification_3 = HashShardingSpecification.fetch(3)
        hash_sharding_specification_4 = HashShardingSpecification.fetch(4)
        hash_sharding_specification_5 = HashShardingSpecification.fetch(5)
        hash_sharding_specifications = HashShardingSpecification.list(1)

        #list does not return the hashing specifications in order of shard_id,
        #hence a direct comparison is not posssible.
        self.assertTrue(
            self.hash_sharding_specification_in_list(
                hash_sharding_specification_1,
                hash_sharding_specifications
            )
        )
        self.assertTrue(
            self.hash_sharding_specification_in_list(
                hash_sharding_specification_2,
                hash_sharding_specifications
            )
        )
        self.assertTrue(
            self.hash_sharding_specification_in_list(
                hash_sharding_specification_3,
                hash_sharding_specifications
            )
        )
        self.assertTrue(
            self.hash_sharding_specification_in_list(
                hash_sharding_specification_4,
                hash_sharding_specifications
            )
        )
        self.assertTrue(
            self.hash_sharding_specification_in_list(
                hash_sharding_specification_5,
                hash_sharding_specifications
            )
        )

    def hash_sharding_specification_in_list(self,
                                            hash_sharding_spec,
                                            hash_sharding_specification_list
                                            ):
        """Verify if the given hash sharding specification is present in
        the list of hash sharding specifications.

        :param hash_sharding_spec: The hash sharding specification that
            needs to be lookedup.
        :param hash_sharding_specification_list: The list of hash sharding
            specifications

        :return: True if the hash sharding specification is present.
                False otherwise.
        """
        for i in range(0, len(hash_sharding_specification_list)):
            if ShardingUtils.compare_hash_specifications(
                hash_sharding_spec,
                hash_sharding_specification_list[i]
            ):
                return True
        return False

    def tearDown(self):
        """Tear down the state store setup.
        """
        tests.utils.cleanup_environment()
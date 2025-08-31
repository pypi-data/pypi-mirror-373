# ------------------------------------------------------------------------------------------------------------
# Copyright (c) 2025 Gunivers
#
# This file is part of the Bookshelf project (https://github.com/mcbookshelf/bookshelf).
#
# This source code is subject to the terms of the Mozilla Public License, v. 2.0.
# If a copy of the MPL was not distributed with this file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Conditions:
# - You may use this file in compliance with the MPL v2.0
# - Any modifications must be documented and disclosed under the same license
#
# For more details, refer to the MPL v2.0.
# ------------------------------------------------------------------------------------------------------------

scoreboard players set @s bs.tmin 2147483647
execute store result score $raycast.piercing bs.lambda run data get storage bs:data raycast.piercing
execute store result score #raycast.max_distance bs.data run data get storage bs:data raycast.max_distance 1000
execute store result score #raycast.btmin bs.data store result score #raycast.etmin bs.data run scoreboard players set #raycast.tmin bs.data 2147483647
data modify storage bs:lambda raycast set value {distance:0d,hit_normal:[0,0,0]}
execute positioned ^ ^ ^ summon minecraft:marker run function bs.raycast:recurse/init
data modify storage bs:out raycast set from storage bs:lambda raycast
scoreboard players reset @e[distance=..255,scores={bs.tmin=0..}] bs.tmin
return run execute unless score #raycast.tmin bs.data matches 2147483647

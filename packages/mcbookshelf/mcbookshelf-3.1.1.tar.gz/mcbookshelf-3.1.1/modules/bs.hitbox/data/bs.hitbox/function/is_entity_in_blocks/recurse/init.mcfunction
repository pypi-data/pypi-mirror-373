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

scoreboard players operation #l bs.ctx /= 10000000 bs.const
scoreboard players operation #l bs.ctx *= 10000000 bs.const
scoreboard players operation #x bs.ctx -= #l bs.ctx
scoreboard players operation #i bs.ctx -= #l bs.ctx

scoreboard players operation #m bs.ctx /= 10000000 bs.const
scoreboard players operation #m bs.ctx *= 10000000 bs.const
scoreboard players operation #y bs.ctx -= #m bs.ctx
scoreboard players operation #j bs.ctx -= #m bs.ctx

scoreboard players operation #n bs.ctx /= 10000000 bs.const
scoreboard players operation #n bs.ctx *= 10000000 bs.const
scoreboard players operation #z bs.ctx -= #n bs.ctx
scoreboard players operation #k bs.ctx -= #n bs.ctx

$execute at @s align xyz positioned ~$(x) ~$(y) ~$(z) run return run function bs.hitbox:is_entity_in_blocks/recurse/x

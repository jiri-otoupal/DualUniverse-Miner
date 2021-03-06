#
#      @@@  @@@@@@  @@@@@@@  @@@  @@@ @@@@@@@@ @@@
#      @@! @@!  @@@ @@!  @@@ @@!  @@@ @@!      @@!
#      !!@ @!@  !@! @!@  !@! @!@  !@! @!!!:!   @!!
#  .  .!!  !!:  !!! !!:  !!!  !: .:!  !!:      !!:
#  ::.::    : :. :  :: :  :     ::    : :: ::  : ::.: :
#

"""

Config

Modify only when you know ,what you are actually doing !

"""
import logging

# ---------------------------- Debug ------------------------------#

only_debug = False  # This results in not mining on request
dont_turn_debug = False  # This results in not rotating camera on request
dont_move = False  # This results in not moving on request

# ---------------------------- Debug ------------------------------#


# ------------------------- Bot Settings ---------------------------#
mining_time_sphere = 1.9  # Seconds to wait while spreading mining sphere
failsafe_timeout = 15  # Cycles in which timeout and do some movement to unblock
cloud = False  # Cloud computing ( DISABLED )
prediction_batch_size = 8  # Higher takes more memory and little speed up
ore_threshold = 0.45  # Percent
full_auto = False  # Will increase mining radius ( SLOW )
model_to_use_ores = "models/ores_s_v1_soft"  # Model to use for recognition / previous ores_a_v4_soft
ore_list = ["ore"]  # whitelist of ores
log_level = logging.INFO  # Log leve ( Debug will show not only bot logs )
rotation_angle = 2  # degrees ( Smallest degree in sensitivity range is 2 )
forward_time = 1  # seconds
machine_learning = False

# Performance impact settings
#   Higher Number = Higher Impact on Performance and slower


circle_index_loop = 3  # Loops for circle modifying
circle_index_tempo = 0.1  # tempo in which to decrease panes of area that is searched
# ------------------------- Bot Settings ---------------------------#


logo = r"""                                                     
    @@@  @@@@@@  @@@@@@@  @@@  @@@ @@@@@@@@ @@@      
    @@! @@!  @@@ @@!  @@@ @@!  @@@ @@!      @@!      
    !!@ @!@  !@! @!@  !@! @!@  !@! @!!!:!   @!!      
.  .!!  !!:  !!! !!:  !!!  !: .:!  !!:      !!:      
::.::    : :. :  :: :  :     ::    : :: ::  : ::.: : 
                                                     """;

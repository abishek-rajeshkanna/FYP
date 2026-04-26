# env/lane_paths.py

def generate_lane_paths(cx, cy):

    lane_width = 65
    l0 = 97
    l1 = 32

    paths = {

    "SOUTH":{

        0:{
            "STRAIGHT":[(cx-l0, cy+400),(cx-l0, cy+120),(cx-l0, cy-120),(cx-l0, cy-400)],
            "LEFT":[(cx-l0, cy+400),(cx-l0, cy+120),(cx-90,cy+60),(cx-120,cy),(cx-150,cy-60),(cx-200,cy-120)],
            "RIGHT":[(cx-l0, cy+400),(cx-l0, cy+120),(cx-10,cy+80),(cx+60,cy+20),(cx+120,cy-32)],
            "UTURN":[(cx-l0, cy+400),(cx-l0, cy+120),(cx-80,cy+80),(cx-100,cy),(cx-80,cy-80),(cx-l0, cy+120)]
        },

        1:{
            "STRAIGHT":[(cx-l1, cy+400),(cx-l1, cy+120),(cx-l1, cy-120),(cx-l1, cy-400)],
            "LEFT":[(cx-l1, cy+400),(cx-l1, cy+120),(cx-60,cy+60),(cx-90,cy),(cx-120,cy-60),(cx-160,cy-120)],
            "RIGHT":[(cx-l1, cy+400),(cx-l1, cy+120),(cx+20,cy+70),(cx+80,cy),(cx+120,cy-97)],
            "UTURN":[(cx-l1, cy+400),(cx-l1, cy+120),(cx-60,cy+60),(cx-60,cy),(cx-60,cy-60),(cx-l1, cy+120)]
        }

    },


    "NORTH":{

        0:{
            "STRAIGHT":[(cx+l0, cy-400),(cx+l0, cy-120),(cx+l0, cy+120),(cx+l0, cy+400)],
            "LEFT":[(cx+l0, cy-400),(cx+l0, cy-120),(cx+90,cy-60),(cx+120,cy),(cx+150,cy+60),(cx+200,cy+120)],
            "RIGHT":[(cx+l0, cy-400),(cx+l0, cy-120),(cx+10,cy-80),(cx-60,cy-20),(cx-120,cy+32)],
            "UTURN":[(cx+l0, cy-400),(cx+l0, cy-120),(cx+80,cy-80),(cx+100,cy),(cx+80,cy+80),(cx+l0, cy-120)]
        },

        1:{
            "STRAIGHT":[(cx+l1, cy-400),(cx+l1, cy-120),(cx+l1, cy+120),(cx+l1, cy+400)],
            "LEFT":[(cx+l1, cy-400),(cx+l1, cy-120),(cx+60,cy-60),(cx+90,cy),(cx+120,cy+60),(cx+160,cy+120)],
            "RIGHT":[(cx+l1, cy-400),(cx+l1, cy-120),(cx-20,cy-70),(cx-80,cy),(cx-120,cy+97)],
            "UTURN":[(cx+l1, cy-400),(cx+l1, cy-120),(cx+60,cy-60),(cx+60,cy),(cx+60,cy+60),(cx+l1, cy-120)]
        }

    },


    "WEST":{

        0:{
            "STRAIGHT":[(cx-400, cy-l0),(cx-120, cy-l0),(cx+120, cy-l0),(cx+400, cy-l0)],
            "LEFT":[(cx-400, cy-l0),(cx-120, cy-l0),(cx-60,cy-90),(cx,cy-120),(cx+60,cy-150),(cx+120,cy-200)],
            "RIGHT":[(cx-400, cy-l0),(cx-120, cy-l0),(cx-80,cy-10),(cx-20,cy+60),(cx+32,cy+120)],
            "UTURN":[(cx-400, cy-l0),(cx-120, cy-l0),(cx-80,cy-80),(cx,cy-100),(cx+80,cy-80),(cx-120, cy-l0)]
        },

        1:{
            "STRAIGHT":[(cx-400, cy-l1),(cx-120, cy-l1),(cx+120, cy-l1),(cx+400, cy-l1)],
            "LEFT":[(cx-400, cy-l1),(cx-120, cy-l1),(cx-60,cy-60),(cx,cy-90),(cx+60,cy-120),(cx+120,cy-160)],
            "RIGHT":[(cx-400, cy-l1),(cx-120, cy-l1),(cx-70,cy+20),(cx,cy+80),(cx+97,cy+120)],
            "UTURN":[(cx-400, cy-l1),(cx-120, cy-l1),(cx-60,cy-60),(cx,cy-60),(cx+60,cy-60),(cx-120, cy-l1)]
        }

    },


    "EAST":{

        0:{
            "STRAIGHT":[(cx+400, cy+l0),(cx+120, cy+l0),(cx-120, cy+l0),(cx-400, cy+l0)],
            "LEFT":[(cx+400, cy+l0),(cx+120, cy+l0),(cx+60,cy+90),(cx,cy+120),(cx-60,cy+150),(cx-120,cy+200)],
            "RIGHT":[(cx+400, cy+l0),(cx+120, cy+l0),(cx+80,cy+10),(cx+20,cy-60),(cx-32,cy-120)],
            "UTURN":[(cx+400, cy+l0),(cx+120, cy+l0),(cx+80,cy+80),(cx,cy+100),(cx-80,cy+80),(cx+120, cy+l0)]
        },

        1:{
            "STRAIGHT":[(cx+400, cy+l1),(cx+120, cy+l1),(cx-120, cy+l1),(cx-400, cy+l1)],
            "LEFT":[(cx+400, cy+l1),(cx+120, cy+l1),(cx+60,cy+60),(cx,cy+90),(cx-60,cy+120),(cx-120,cy+160)],
            "RIGHT":[(cx+400, cy+l1),(cx+120, cy+l1),(cx+70,cy-20),(cx,cy-80),(cx-97,cy-120)],
            "UTURN":[(cx+400, cy+l1),(cx+120, cy+l1),(cx+60,cy+60),(cx,cy+60),(cx-60,cy+60),(cx+120, cy+l1)]
        }

    }

    }

    return paths
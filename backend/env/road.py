import pygame


class Road:

    def __init__(self, width, height):

        self.width = width
        self.height = height

        self.cx = width // 2
        self.cy = height // 2

        self.road_width = 260
        self.lane_width = 65

        self.font = pygame.font.SysFont("Arial", 14)
        self.big_font = pygame.font.SysFont("Arial", 15, True)
        self.metric_font = pygame.font.SysFont("Arial", 14)

        self.blink = True
        self.blink_timer = pygame.time.get_ticks()

        # SAFE ZONE VARIABLES
        self.SAFE_LEFT_OFFSET = 360
        self.SAFE_RIGHT_OFFSET = 360
        self.SAFE_TOP_OFFSET = 260
        self.SAFE_BOTTOM_OFFSET = 260

        # EMV MESSAGE SYSTEM
        self.messages = {
            "WEST": "SAFE ZONE ACTIVE",
            "EAST": "SAFE ZONE ACTIVE",
            "NORTH": "SAFE ZONE ACTIVE",
            "SOUTH": "SAFE ZONE ACTIVE"
        }

        self.scroll = {
            "WEST": 0,
            "EAST": 0,
            "NORTH": 0,
            "SOUTH": 0
        }

        self.scroll_speed = 2

    # --------------------------------------------------

    def set_emv_message(self, direction, msg):

        if direction in self.messages:
            self.messages[direction] = msg

    # --------------------------------------------------

    def draw_background(self, screen):
        screen.fill((34, 139, 34))

    # --------------------------------------------------

    def draw_roads(self, screen):

        cx = self.cx
        cy = self.cy
        rw = self.road_width

        pygame.draw.rect(screen,(60,60,60),(cx-rw//2,0,rw,self.height))
        pygame.draw.rect(screen,(60,60,60),(0,cy-rw//2,self.width,rw))

        pygame.draw.rect(screen,(255,255,255),(cx-rw//2,0,2,self.height))
        pygame.draw.rect(screen,(255,255,255),(cx+rw//2,0,2,self.height))
        pygame.draw.rect(screen,(255,255,255),(0,cy-rw//2,self.width,2))
        pygame.draw.rect(screen,(255,255,255),(0,cy+rw//2,self.width,2))

    # --------------------------------------------------

    def draw_lane_markings(self, screen):

        cx=self.cx
        cy=self.cy
        lane=65

        for y in range(0,self.height,40):
            pygame.draw.rect(screen,(255,215,0),(cx-lane-2,y,4,20))
            pygame.draw.rect(screen,(255,215,0),(cx+lane-2,y,4,20))

        for x in range(0,self.width,40):
            pygame.draw.rect(screen,(255,215,0),(x,cy-lane-2,20,4))
            pygame.draw.rect(screen,(255,215,0),(x,cy+lane-2,20,4))

    # --------------------------------------------------

    def draw_dividers(self,screen):

        cx=self.cx
        cy=self.cy

        pygame.draw.line(screen,(255,0,0),(cx,0),(cx,self.height),4)
        pygame.draw.line(screen,(255,0,0),(0,cy),(self.width,cy),4)

    # --------------------------------------------------

    def draw_crosswalk(self,screen):

        cx=self.cx
        cy=self.cy
        size=120

        for i in range(-size,size,15):

            pygame.draw.rect(screen,(255,255,255),(cx-130,cy+i,20,6))
            pygame.draw.rect(screen,(255,255,255),(cx+110,cy+i,20,6))

            pygame.draw.rect(screen,(255,255,255),(cx+i,cy-130,6,20))
            pygame.draw.rect(screen,(255,255,255),(cx+i,cy+110,6,20))

    # --------------------------------------------------
    # SAFE ZONE LINES
    # --------------------------------------------------

    def draw_safe_zones(self, screen):

        cx = self.cx
        cy = self.cy
        rw = self.road_width

        PINK = (255,105,180)

        pygame.draw.line(screen,PINK,(cx-self.SAFE_LEFT_OFFSET,cy-rw//2),(cx-self.SAFE_LEFT_OFFSET,cy+rw//2),3)
        pygame.draw.line(screen,PINK,(cx+self.SAFE_RIGHT_OFFSET,cy-rw//2),(cx+self.SAFE_RIGHT_OFFSET,cy+rw//2),3)
        pygame.draw.line(screen,PINK,(cx-rw//2,cy-self.SAFE_TOP_OFFSET),(cx+rw//2,cy-self.SAFE_TOP_OFFSET),3)
        pygame.draw.line(screen,PINK,(cx-rw//2,cy+self.SAFE_BOTTOM_OFFSET),(cx+rw//2,cy+self.SAFE_BOTTOM_OFFSET),3)

    # --------------------------------------------------
    # EMV MESSAGE BOARDS
    # --------------------------------------------------

    def draw_emv_boards(self, screen):

        board_w = 170
        board_h = 28

        LIGHT_BLUE = (0,200,255)

        boards = {

            "WEST": (10, self.cy - self.road_width//2 - 170),
            "EAST": (self.width - board_w - 10, self.cy - self.road_width//2 + 400),
            "NORTH": (self.cx - board_w//2 + 220, 140),
            "SOUTH": (self.cx - board_w//2 - 250, self.height - 30)

        }

        for direction,(x,y) in boards.items():

            pygame.draw.rect(screen,(0,0,0),(x,y,board_w,board_h))
            pygame.draw.rect(screen,LIGHT_BLUE,(x,y,board_w,board_h),2)

            text=self.messages[direction]

            surf=self.font.render(text,True,(255,105,180))
            text_width=surf.get_width()

            self.scroll[direction]-=self.scroll_speed

            if self.scroll[direction] < -text_width:
                self.scroll[direction]=board_w

            clip_rect=pygame.Rect(x,y,board_w,board_h)
            screen.set_clip(clip_rect)

            screen.blit(surf,(x+self.scroll[direction],y+6))

            screen.set_clip(None)

    # --------------------------------------------------

    def draw_center_beacon(self,screen):

        now = pygame.time.get_ticks()

        if now - self.blink_timer > 500:
            self.blink = not self.blink
            self.blink_timer = now

        if self.blink:
            pygame.draw.circle(screen,(255,0,0),(self.cx,self.cy),8)

    # --------------------------------------------------

    def draw_signals(self,screen,ev_data):

        cx=self.cx
        cy=self.cy
        offset=80

        phase = ev_data.get("signal_phase","HORIZONTAL_GREEN")
        timer = ev_data.get("signal_timer",0)

        RED=(255,0,0)
        YELLOW=(255,255,0)
        GREEN=(0,255,0)
        OFF=(40,40,40)

        positions=[
            ("TOP",(cx,cy-offset)),
            ("BOTTOM",(cx,cy+offset)),
            ("LEFT",(cx-offset,cy)),
            ("RIGHT",(cx+offset,cy))
        ]

        for side,(x,y) in positions:

            pygame.draw.rect(screen,(0,0,0),(x-10,y-20,20,40))

            if side in ["LEFT","RIGHT"]:

                if phase=="HORIZONTAL_GREEN":
                    r,yel,g = OFF,OFF,GREEN
                elif phase=="HORIZONTAL_YELLOW":
                    r,yel,g = OFF,YELLOW,OFF
                else:
                    r,yel,g = RED,OFF,OFF

            else:

                if phase=="VERTICAL_GREEN":
                    r,yel,g = OFF,OFF,GREEN
                elif phase=="VERTICAL_YELLOW":
                    r,yel,g = OFF,YELLOW,OFF
                else:
                    r,yel,g = RED,OFF,OFF

            pygame.draw.circle(screen,r,(x,y-10),4)
            pygame.draw.circle(screen,yel,(x,y),4)
            pygame.draw.circle(screen,g,(x,y+10),4)

            pygame.draw.rect(screen,(20,20,20),(x-20,y+25,40,18))

            txt=self.font.render(str(timer),True,(0,255,0))
            screen.blit(txt,(x-8,y+27))
    # --------------------------------------------------

    def create_board_surface(self,name,lane_stats,l0,l1):

        board_w=160
        board_h=130

        surf=pygame.Surface((board_w,board_h),pygame.SRCALPHA)

        pygame.draw.rect(surf,(0,0,0),(0,0,board_w,board_h))
        pygame.draw.rect(surf,(0,255,255),(0,0,board_w,board_h),2)

        label=(255,215,0)
        value=(0,255,0)
        header=(0,255,255)

        title=self.big_font.render(name,True,(255,165,0))
        surf.blit(title,(8,5))

        surf.blit(self.font.render("Metric",True,header),(8,30))
        surf.blit(self.font.render("L0",True,header),(105,30))
        surf.blit(self.font.render("L1",True,header),(135,30))

        pygame.draw.line(surf,(0,200,200),(5,45),(155,45),1)

        if l0 in lane_stats:

            s0=lane_stats[l0]
            s1=lane_stats[l1]

            rows=[
                ("Queue",s0["queue"],s1["queue"]),
                ("Cars",s0["cars"],s1["cars"]),
                ("Trucks",s0["trucks"],s1["trucks"]),
                ("Police",s0["police"],s1["police"]),
                ("Amb",s0["ambulance"],s1["ambulance"])
            ]

            y=50

            for txt,a,b in rows:

                surf.blit(self.font.render(txt,True,label),(8,y))
                surf.blit(self.font.render(str(a),True,value),(110,y))
                surf.blit(self.font.render(str(b),True,value),(140,y))

                y+=16

        return surf
    # --------------------------------------------------
    # LED TRAFFIC BOARDS (RESTORED)
    # --------------------------------------------------

    def draw_led_boards(self,screen,lane_stats):

        cx=self.cx
        cy=self.cy
        edge=self.road_width//2

        boards=[

            ("Abharna Shree",(20,cy-edge-140),"H",("W0","W1")),
            ("Vinith",(self.width-180,cy-edge+270),"H",("E0","E1")),
            ("Abishek",(cx-edge-165,5),"TOP",("N0","N1")),
            ("Aravind",(cx-edge-170,self.height-160),"BOTTOM",("S0","S1"))

        ]

        for name,pos,mode,(l0,l1) in boards:

            surf=self.create_board_surface(name,lane_stats,l0,l1)
            screen.blit(surf,pos)

    # --------------------------------------------------
    # NEW DASHBOARD PANEL
    # --------------------------------------------------

    def draw_observation_panel(self,screen,ev_data,lane_stats):

        panel_w=260
        panel_h=200

        x=self.width-panel_w-15
        y=5

        pygame.draw.rect(screen,(0,0,0),(x,y,panel_w,panel_h))
        pygame.draw.rect(screen,(255,0,0),(x,y,panel_w,panel_h),2)

        label=(255,215,0)
        value=(0,255,0)

        title=self.big_font.render("QoS METRICS",True,(0,255,0))
        screen.blit(title,(x+8,y+5))

        q = ev_data.get("qos_display", {})

        yy=y+40

        qos_rows = [
            ("Range (R)", f"{q.get('R', 0)} m"),
            ("Carrier (σ)", f"{q.get('sigma', 0)}"),
            ("Packet (λ)", f"{q.get('lambda', 0)} msg/s"),
            ("Contention", f"{q.get('Wc', 0)} ms")
        ]

        for metric_name, metric_value in qos_rows:
            screen.blit(self.metric_font.render(metric_name, True, label), (x + 10, yy))
            screen.blit(self.metric_font.render(metric_value, True, value), (x + 140, yy))
            yy += 30

    # --------------------------------------------------

    def draw(self,screen,ev_data,lane_stats):

        self.draw_background(screen)
        self.draw_roads(screen)
        self.draw_lane_markings(screen)
        self.draw_dividers(screen)
        self.draw_crosswalk(screen)

        self.draw_safe_zones(screen)
        self.draw_emv_boards(screen)

        self.draw_center_beacon(screen)
        self.draw_signals(screen,ev_data)

        self.draw_led_boards(screen,lane_stats)

        self.draw_observation_panel(screen,ev_data,lane_stats)
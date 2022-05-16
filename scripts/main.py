# Copyright (c) 2022 Dogwaterzx

import pygame
from enemy import *
from functions import Functions
from player import *
from mainClasses import *
from items import *

# Structure organization inspiration from jessmeng on GitHub: https://github.com/jessmeng/CMU-TD-112
# and TechWithTim Youtube Channel and Coding Website: https://techwithtim.net
# title background: https://www.chupamobile.com/ui-graphic-assets/forest-game-background-8298
# game title font made at https://flamingtext.com
# select screen and in game background: https://www.pinterest.com/pin/425097652302713129/
# game over screen rose from: https://clipartpng.com/?165,beautiful-stem-red-rose-png-clipart
# game music from: https://www.youtube.com/watch?v=-sJRx5egXPM

class PygameGame(object):
    def __init__(self):
        # uncomment below and launch game once to reset highscore to 0
        # with open("scores.txt", 'w') as f:
            #f.write('0')
        pygame.init()
        pygame.display.set_caption("Forest Horizon")
        self.w, self.h = 1000, 800
        self.enemies = []
        self.items = []
        self.isGameOver = False
        self.font = pygame.font.Font(None, 72)
        self.font2 = pygame.font.Font(None, 40)
        self.gameOverText = self.font.render('GAME OVER', True, (140, 100, 140))
        self.gameOverTextRect = self.gameOverText.get_rect()
        self.gameOverTextRect.center = (self.w//2, self.h//2)
        self.killed = 0
        self.spawnSpeed1 = 3000
        self.isSelect = False
        self.mainClasses = [Gunner, Wizard]
        self.title = pygame.image.load('title2.png')
        self.title = pygame.transform.scale(self.title, (3*self.w//4, self.h//5))
        self.terrainFrame = 0
        self.gameTerrain = pygame.image.load('bg.png')
        self.gameTerrain = pygame.transform.scale(self.gameTerrain, (self.w, self.h))
        self.gameTerrain.set_alpha(230)
        self.howTo = pygame.image.load('howto3.png')
        self.howTo = pygame.transform.scale(self.howTo, (self.w, self.h))
        self.titleBG = pygame.image.load('forest.jpg')
        self.titleBG = pygame.transform.scale(self.titleBG, (self.w, self.h))
        self.titleFrame = 0
        self.rose = pygame.image.load('rose.png')
        self.rose = pygame.transform.rotozoom(self.rose, 0, 0.3)
        self.roseBox = self.rose.get_rect()
        self.roseBox.center = (self.w//2, self.h//2)
        self.tempRose = self.rose
        self.roseOp = 0
        self.gameOverBG = 10
        self.isTitle = True
        self.isHowTo = False
        self.enemyBullets = []
        self.rocks = []
        self.itemTick = 0
        self.basicBird, self.fastBird, self.tankBird, self.smartBird = True, False, False, False
        self.spawnSpeed1, self.spawnSpeed2, self.spawnSpeed3, self.spawnSpeed4 = 3000, 3000, 3000, 3000
        self.unlockTimer = 0
        self.spawnTimer = 0
        self.isPause = False
        self.testMode = False
        self.highCheck = False
        self.isHigh = False
        self.lastHigh = 0

    def redrawGameWindow(self, win):
        win.fill((255,255,255))
        if self.isTitle:
            self.drawTitleSc(win)
        elif self.isSelect:
            self.selectScreen(win)
        elif self.isHowTo:
            self.howToScreen(win)
        elif self.isGameOver:
            self.gameOverScreen(win)
        else:
            win.blit(self.gameTerrain, (0,0))
            for rock in self.rocks:
                rock.draw(win)
            self.p1.update()
            self.p1.update1(*pygame.mouse.get_pos(),self.w, self.h)
            self.p1.draw(win)
            self.p1.draw1(win)
            self.ultBar(win)
            self.qBar(win)
            self.eBar(win)
            for bullet in self.p1.bullets:
                if isinstance(bullet, WizBullet):
                    bullet.target = Functions.closestIn(bullet, self.enemies)
                if isinstance(bullet, GunnerQBullet):
                    if bullet.isDet:
                        self.p1.bullets.remove(bullet)
                for rock in self.rocks:
                    if bullet.hitbox.colliderect(rock.hitbox):
                        if not isinstance(bullet, FrostOrb) and (not isinstance(bullet, GunnerQBullet) or bullet.isMain == False):
                            self.p1.bullets.remove(bullet)
            for enemy in self.enemies:
                enemy.update(self.p1.x + self.p1.width//2, self.p1.y + self.p1.height//2, self.rocks)
                self.enemyProjectile(enemy)
                if isinstance(self.p1, Wizard) and self.p1.isQ:
                    self.wizQ(enemy)
            for enemy in self.enemies:            
                enemy.draw(win)
            for item in self.items:
                item.update()
                self.itemEffs(item)
                if item.timer <= 0:
                    self.items.remove(item)
            for item in self.items:
                item.draw(win)
            for bullet in self.enemyBullets:
                self.checkPlayerHit(bullet)
            if self.p1.hp <= 0:
                self.highCheck = False
                self.isGameOver = True
                self.terrainFrame = 0
                self.roseOp = 0
                self.gameOverBG = 10
        pygame.display.update()

    def howToScreen(self, win):
        mouseX, mouseY = pygame.mouse.get_pos()
        if mouseX > 2*self.w//5 and mouseX < 3* self.w //5 and mouseY > 14*self.h//17 and mouseY < 16 *self.h//17:
            color = (200, 250, 200)
        else:
            color = (100, 150, 100)
        win.blit(self.howTo, (0,0))
        pygame.draw.rect(win, color, (2*self.w//5, 14*self.h//17, self.w//5, 2*self.h//17))
        backText = self.font2.render("Back", True, (0,0,0))
        backTextRect = backText.get_rect()
        backTextRect.center = (self.w//2, 15*self.h//17)
        win.blit(backText, backTextRect)

    def drawTitleSc(self, win):
        self.titleFrame += 1
        win.blit(self.titleBG, (self.titleFrame % self.w,0))
        win.blit(self.titleBG, (self.titleFrame % self.w -self.w,0))
        hitbox = self.title.get_rect()
        hitbox.center = (self.w//2, 2*self.h//5)
        win.blit(self.title, hitbox)
        mouseX, mouseY = pygame.mouse.get_pos()
        if mouseX > 2*self.w//5 and mouseX < 3* self.w //5 and mouseY > 21*self.h//36 and mouseY < 23 *self.h//36:
            color1 = (200, 250, 200)
        else:
            color1 = (100, 150, 100)
        if mouseX > 2*self.w//5 and mouseX < 3* self.w //5 and mouseY > 23*self.h//36 and mouseY < 25 *self.h//36:
            color2 = (200, 250, 200)
        else: 
            color2 = (100, 150, 100)
        pygame.draw.rect(win, color1, (2*self.w//5, 21*self.h//36, self.w//5, self.h//18))
        startText = self.font2.render("Start Game", True, (0,0,0))
        startTextRect = startText.get_rect()
        startTextRect.center = (self.w//2, 11*self.h//18)
        win.blit(startText, startTextRect)
        pygame.draw.rect(win, color2, (2*self.w//5, 23*self.h//36, self.w//5, self.h//18))
        howText = self.font2.render("How To Play", True, (0,0,0))
        howTextRect = howText.get_rect()
        howTextRect.center = (self.w//2, 12*self.h//18)
        win.blit(howText, howTextRect)

    def itemEffs(self, item):
        if item.hitbox.colliderect(self.p1.hitbox):
            if isinstance(item, HealthPack):
                self.items.remove(item)
                self.p1.hp += item.healing
                if isinstance(item, Speed):
                    self.p1.speed += 1.5

    def wizQ(self, enemy):
        if self.p1.qHitBox.colliderect(enemy.hitbox):
            if enemy.wizQTimer == 0:
                enemy.hp -= self.p1.qDmg
                enemy.wizQTimer = 70

    def selectScreen(self, win):
        self.terrainFrame += 3
        win.blit(self.gameTerrain, (self.terrainFrame % self.w,0))
        win.blit(self.gameTerrain, (self.terrainFrame % self.w -self.w,0))
        f = pygame.font.Font(None, 90)
        t = f.render("Select Your Class", True, (200,200,200))
        tRect = t.get_rect()
        tRect.center = (self.w//2, self.h//5)
        win.blit(t, tRect)
        numbMain = len(self.mainClasses)
        #margins are 1/10 of cell size, there are n+1 margins
        # (n+1)*x + n*10x = (11n + 1) * x
        marginW = self.w//(11*numbMain + 1)
        for i in range(numbMain):
            start = (i + 1) * marginW + i * 10 * marginW
            pygame.draw.rect(win, (200,200,200), (start, 5*self.h//16, 10*marginW, 3*self.h//5))
            if not isinstance(self.mainClasses[i], int):
                char = self.mainClasses[i].player.convert_alpha()
                char = pygame.transform.scale(char, (9*marginW, self.h//2))
                charRect = char.get_rect()
                charRect.center = (start + 5*marginW, 5*self.h//16+(3*self.h//5)//2)
                win.blit(char,charRect)
        mouseX, mouseY = pygame.mouse.get_pos()
        for i in range(numbMain):
            startX = (i + 1) * marginW + i * 10 * marginW
            endX = startX + 10 * marginW
            startY = 5*self.h//16
            endY = startY + 3*self.h//5
            if mouseX > startX and mouseX < endX and mouseY > startY and mouseY < endY:
                desc = pygame.transform.scale(self.mainClasses[i].desc, (10*marginW, 3*self.h//5))
                win.blit(desc, (startX, startY))

    def enemyProjectile(self, enemy):
        for bullet in self.p1.bullets:
            if bullet.hitbox.colliderect(enemy.hitbox):
                enemy.hp -= bullet.damage
                if isinstance(bullet, WizBullet):
                    enemy.isSlow = True
                if isinstance(bullet, FrostOrb):
                    enemy.isSupSlow = True
                if not isinstance(bullet, FrostOrb) and (not isinstance(bullet, GunnerQBullet) or bullet.isMain == False):
                    self.p1.bullets.remove(bullet)
        if isinstance(self.p1, Gunner):
            for exp in self.p1.explosions:
                if exp.hitbox.colliderect(enemy.hitbox):
                    if enemy.canExp == True:
                        enemy.hp -= exp.damage
                        enemy.expTimer = 50
                        enemy.canExp = False
        if enemy.hp <= 0:
            self.enemies.remove(enemy)
            self.killed += 1
            if self.p1.isUlt == False:
                self.p1.ultAmmo += 50
        elif enemy.hitbox.colliderect(self.p1.hitbox):
            self.p1.hp -= enemy.damage
            self.enemies.remove(enemy)

    def ultBar(self, win):
        ammoPerc = self.p1.ultAmmo / self.p1.maxUltAmmo
        if ammoPerc == 1:
            color = (204, 204, 0)
        else:
            blue = 180 - 150 * ammoPerc
            color = (255,255, blue)
        pygame.draw.rect(win, color, (self.w//10, self.h//20, 4*ammoPerc*self.w//5, self.h//20))
        pygame.draw.rect(win, (204,204,0), (self.w//10, self.h//20, 4*self.w//5, self.h//20), width = 3)
        if ammoPerc == 1:
            f = pygame.font.Font(None, 30)
            t = f.render("PRESS R TO USE SPECIAL", True, (70,70,0))
            tRect = t.get_rect()
            tRect.center = (self.w//2, 3*self.h//40)
            win.blit(t, tRect)

    def qBar(self, win):
        qPerc = self.p1.qAmmo / self.p1.maxQAmmo
        pygame.draw.rect(win, (50,100,200), (self.w//40, 15*self.h//20, qPerc*self.w//5, self.h//40))
        pygame.draw.rect(win, (50,100,140), (self.w//40, 15*self.h//20, self.w//5, self.h//40), width = 2)
        f = pygame.font.Font(None, 30)
        if qPerc == 1:
            color = (196,236,255)
        else:
            color = (160, 160, 160)
        t = f.render("Q", True, color)
        tRect = t.get_rect()
        tRect.center = (self.w//80, 61*self.h//80)
        win.blit(t, tRect)
    
    def eBar(self, win):
        ePerc = self.p1.eAmmo / self.p1.maxEAmmo
        pygame.draw.rect(win, (100,160,20), (self.w//40, 16*self.h//20, ePerc*self.w//5, self.h//40))
        pygame.draw.rect(win, (100,170,20), (self.w//40, 16*self.h//20, self.w//5, self.h//40), width = 2)
        f = pygame.font.Font(None, 30)
        if ePerc == 1:
            color = (214,255,226)
        else:
            color = (160, 160, 160)
        t = f.render("E", True, color)
        tRect = t.get_rect()
        tRect.center = (self.w//80, 65*self.h//80)
        win.blit(t, tRect)

    def gameOverScreen(self, win):
        if self.roseOp < 405:
            self.roseOp += 2
        if self.gameOverBG < 210:
            self.gameOverBG += 1
        self.rose.set_alpha(255- abs(150-self.roseOp))
        win.fill((self.gameOverBG,self.gameOverBG,self.gameOverBG))
        win.blit(self.rose, self.roseBox)
        scoreText = self.font2.render(f"Enemies killed: {self.killed}", True, (150, 100, 150))
        scoreTextRect = scoreText.get_rect()
        scoreTextRect.center = (self.w//2, 5*self.h//8)
        win.blit(self.gameOverText, self.gameOverTextRect)
        win.blit(scoreText, scoreTextRect)
        pygame.draw.rect(win, (200,90,170), (2*self.w//5, 5*self.h//7, self.w//5, self.h//7), width = 3)
        restText = self.font2.render("RESTART", True, (200,90,170))
        restTextRect = restText.get_rect()
        restTextRect.center = (self.w//2, 11*self.h//14)
        if not self.testMode:
            if self.highCheck == False:
                with open("scores.txt", 'r') as f:
                    lines = f.readlines()
                    highscore = int(lines[0])
                with open("scores.txt", 'w') as f:
                    if self.killed > highscore:
                        f.write(str(self.killed))
                        self.isHigh = True
                    else:
                        f.write(str(highscore))
                        self.lastHigh = highscore
                        self.isHigh = False
                self.highCheck = True
            if self.isHigh:
                highStr = "NEW HIGHSCORE!!!"
                font = pygame.font.Font(None, 80)
                color = (180,100,220)
            else:
                highStr = f"(Current Highscore: {self.lastHigh})"
                font = pygame.font.Font(None, 40)
                color = (100,100,100)
            highText = font.render(highStr, True, color)
            highTextRect = highText.get_rect()
            highTextRect.center = (self.w//2, self.h//4)
            win.blit(highText, highTextRect)
        win.blit(restText, restTextRect)

    def isKeyHeld(self, key):
        keys = pygame.key.get_pressed()
        if keys[key]:
            return True
        return False

    def keyHeld(self, key):
        if self.isGameOver == False:
            if key == pygame.K_w:
                self.p1.move(self.rocks,'up')
            if key == pygame.K_s:
                self.p1.move(self.rocks,'down')
            if key == pygame.K_a:
                self.p1.move(self.rocks,'left')
            if key == pygame.K_d:
                self.p1.move(self.rocks,'right')

    def keyPressed(self, key, mod):
        if key == pygame.K_ESCAPE:
            self.isTitle = True
            self.isGameOver = False
            self.isSelect = False
            self.isHowTo = False
        if self.isGameOver == False:
            if key == pygame.K_r:
                self.p1.startUlt()
            if key == pygame.K_q:
                self.p1.qSkill(*pygame.mouse.get_pos())
            if key == pygame.K_e:
                self.p1.eSkill(*pygame.mouse.get_pos(), self.rocks)
            if not self.isTitle and not self.isSelect and not self.isHowTo and key == pygame.K_p:
                self.isPause = not self.isPause
            if self.testMode:
                mx, my = pygame.mouse.get_pos()
                if key == pygame.K_1:
                    self.enemies.append(Enemy(mx, my, 65))
                if key == pygame.K_2:
                    self.enemies.append(Enemy2(mx, my, 65))
                if key == pygame.K_3:
                    self.enemies.append(Enemy3(mx, my, 100))
                if key == pygame.K_4:
                    self.enemies.append(Enemy4(mx, my, 70))
                

    def mouseUp(self, mouseX, mouseY, button):
        if button == 1:
            self.p1.isShoot = False

    def mousePressed(self, mouseX, mouseY, button):
        if button == 1:
            self.p1.isShoot = True
        if self.isGameOver:
            if mouseX > 2*self.w//5 and mouseX < 3* self.w //5 and mouseY > 5*self.h//7 and mouseY < 6*self.h//7:
                self.restart()
        elif self.isTitle:
            if mouseX > 2*self.w//5 and mouseX < 3* self.w //5 and mouseY > 21*self.h//36 and mouseY < 23 *self.h//36:
                self.isTitle = False
                self.isSelect = True
            if mouseX > 2*self.w//5 and mouseX < 3* self.w //5 and mouseY > 23*self.h//36 and mouseY < 25 *self.h//36:
                self.isTitle = False
                self.isHowTo = True
        elif self.isHowTo:
            if mouseX > 2*self.w//5 and mouseX < 3* self.w //5 and mouseY > 14*self.h//17 and mouseY < 16 *self.h//17:
                self.isHowTo = False
                self.isTitle = True
        elif self.isSelect:
            numbMain = len(self.mainClasses)
            marginW = self.w//(11*numbMain + 1)
            for i in range(numbMain):
                startX = (i + 1) * marginW + i * 10 * marginW
                endX = startX + 10 * marginW
                startY = 5*self.h//16
                endY = startY + 3*self.h//5
                if mouseX > startX and mouseX < endX and mouseY > startY and mouseY < endY:
                    if self.isKeyHeld(pygame.K_c):
                        self.testMode = True
                    else:
                        self.testMode = False
                    self.spawnPlayer(self.mainClasses[i])
                    self.isSelect = False
                    break
    
    def restart(self):
        self.isGameOver = False
        self.isSelect = True
  
    def mouseMoved(self, mouseX, mouseY):
        if mouseX < self.p1.x + self.p1.width//2:
            self.p1.left = True
        else:
            self.p1.left = False

    def refreshUserEvents(self):
        self.itemTick = 0
        self.spawnSpeed1, self.spawnSpeed2, self.spawnSpeed3, self.spawnSpeed4 = 2600, 3000, 3000, 3000
        self.unlockTimer = 0
        self.spawnTimer = 0
        self.basicBird, self.fastBird, self.tankBird, self.smartBird = True, False, False, False
        SPAWNENEMY = pygame.USEREVENT
        pygame.time.set_timer(SPAWNENEMY,self.spawnSpeed1)
        SPAWNITEM = pygame.USEREVENT + 1
        pygame.time.set_timer(SPAWNITEM, 1000)
        UNLOCKENEMY = pygame.USEREVENT + 2
        pygame.time.set_timer(UNLOCKENEMY, 4000)
        SPEEDUP = pygame.USEREVENT + 3
        pygame.time.set_timer(SPEEDUP, 5000)
        SPAWNENEMY2 = pygame.USEREVENT + 4
        pygame.time.set_timer(SPAWNENEMY2,self.spawnSpeed2)
        SPAWNENEMY3 = pygame.USEREVENT + 5
        pygame.time.set_timer(SPAWNENEMY3,self.spawnSpeed3)
        SPAWNENEMY4 = pygame.USEREVENT + 6
        pygame.time.set_timer(SPAWNENEMY4,self.spawnSpeed4)
        
    def spawnPlayer(self, mainClass):
        self.p1 = mainClass(self.w//2 - 100/2,self.h//2 - 50,100,100,self.w,self.h)
        self.refreshUserEvents()
        self.rocks = []
        self.enemies = []
        self.items = []
        self.killed = 0
        self.isPause = False
        while len(self.rocks) < 4:
            newRock = Rock.newRock(self.w,self.h, 110)
            add = True
            for rock in self.rocks:
                if rock.hitbox.colliderect(newRock.hitbox) or Functions.getDist(rock, newRock) < self.p1.height + rock.size:
                    add = False
            if self.p1.hitbox.colliderect(newRock.hitbox):
                add = False
            if add:
                self.rocks.append(newRock)

    def spawnEnemy(self):
        if self.basicBird:
            self.enemies.append(Enemy.newEnemy(self.w,self.h,65))
    def spawnEnemy2(self):
        if self.fastBird:
            self.enemies.append(Enemy2.newEnemy(self.w,self.h,65))
    def spawnEnemy3(self):
        if self.tankBird:
            self.enemies.append(Enemy3.newEnemy(self.w,self.h,120))
    def spawnEnemy4(self):
        if self.smartBird:
            self.enemies.append(Enemy4.newEnemy(self.w,self.h,70))

    def itemDrop(self):
        self.itemTick += 1
        if self.itemTick % 7 == 0:
            self.items.append(HealthPack(self.w, self.h, self.rocks))
        if self.itemTick % 15 == 0:
            if self.p1.speed < 12:
                self.items.append(Speed(self.w,self.h, self.rocks))
                
    def unlockEnemy(self):
        self.unlockTimer += 1
        if self.unlockTimer == 7:
            self.fastBird = True
        if self.unlockTimer == 12:
            self.tankBird = True
        if self.unlockTimer == 14:
            self.fastBird = False
        if self.unlockTimer == 17:
            self.smartBird = True
        if self.unlockTimer == 18:
            self.fastBird = True
        if self.unlockTimer == 20:
            self.fastBird = False
        if self.unlockTimer == 23:
            self.fastBird = True
        if self.unlockTimer == 23:
            self.tankBird = False
        if self.unlockTimer == 27:
            self.tankBird = True



    def speedUpSpawn(self):
        if self.spawnSpeed1 > 1300 and not self.smartBird:
            self.spawnSpeed1 = int(self.spawnSpeed1*0.90)
            SPAWNENEMY = pygame.USEREVENT
            pygame.time.set_timer(SPAWNENEMY,self.spawnSpeed1)
        elif self.tankBird:
            self.spawnSpeed1 = 1800
            SPAWNENEMY = pygame.USEREVENT
            pygame.time.set_timer(SPAWNENEMY,self.spawnSpeed1)
        elif self.smartBird:
            self.spawnSpeed1 = 3000
            SPAWNENEMY = pygame.USEREVENT
            pygame.time.set_timer(SPAWNENEMY,self.spawnSpeed1)
        if self.fastBird and self.spawnSpeed2 > 1000:
            self.spawnSpeed2 = int(self.spawnSpeed2 * 0.93)
            SPAWNENEMY2 = pygame.USEREVENT + 4
            pygame.time.set_timer(SPAWNENEMY2,self.spawnSpeed2)
        elif self.smartBird:
            self.spawnSpeed2 = 1400
            SPAWNENEMY2 = pygame.USEREVENT + 4
            pygame.time.set_timer(SPAWNENEMY2,self.spawnSpeed2)
        if self.tankBird and self.spawnSpeed3 > 1200:
            self.spawnSpeed2 = int(self.spawnSpeed2 * 0.90)
            SPAWNENEMY3 = pygame.USEREVENT + 5
            pygame.time.set_timer(SPAWNENEMY3,self.spawnSpeed3)
        elif self.smartBird:
            self.spawnSpeed2 = 2000
            SPAWNENEMY3 = pygame.USEREVENT + 5
            pygame.time.set_timer(SPAWNENEMY3,self.spawnSpeed3)
        if self.smartBird and self.spawnSpeed4 > 1000:
            self.spawnSpeed4 = int(self.spawnSpeed4 * 0.90)
            SPAWNENEMY4 = pygame.USEREVENT + 6
            pygame.time.set_timer(SPAWNENEMY4,self.spawnSpeed4)
            
    def run(self):
        screen = pygame.display.set_mode((self.w,self.h))
        clock = pygame.time.Clock()
        pygame.mixer.init()
        pygame.mixer.music.load('forestmusic.ogg')
        pygame.mixer.music.play(-1)
        SPAWNENEMY = pygame.USEREVENT
        SPAWNITEM = pygame.USEREVENT + 1
        UNLOCKENEMY = pygame.USEREVENT + 2
        SPEEDUP = pygame.USEREVENT + 3
        SPAWNENEMY2 = pygame.USEREVENT + 4
        SPAWNENEMY3 = pygame.USEREVENT + 5
        SPAWNENEMY4 = pygame.USEREVENT + 6
        self.spawnPlayer(Gunner) 
        pygame.mouse.set_cursor(*pygame.cursors.broken_x)
        running = True
        while running:
            while self.isPause:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                        self.isPause = not self.isPause
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEMOTION:
                    self.mouseMoved(*event.pos)
                if event.type == SPAWNENEMY:
                    if not self.testMode:
                        self.spawnEnemy()
                if event.type == SPAWNENEMY2:
                    if not self.testMode:
                        self.spawnEnemy2()
                if event.type == SPAWNENEMY3:
                    if not self.testMode:
                        self.spawnEnemy3()
                if event.type == SPAWNENEMY4:
                    if not self.testMode:
                        self.spawnEnemy4()
                if event.type == UNLOCKENEMY:
                    self.unlockEnemy()
                if event.type == SPAWNITEM:
                    self.itemDrop()
                if event.type == SPEEDUP:
                    self.speedUpSpawn()
                if event.type == pygame.KEYDOWN:
                    self.keyPressed(event.key, event.mod)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.mousePressed(*event.pos, event.button)
                if event.type == pygame.MOUSEBUTTONUP:
                    self.mouseUp(*event.pos, event.button)
            for heldKeys in [pygame.K_w, pygame.K_a, pygame.K_s, pygame.K_d]:
                    if self.isKeyHeld(heldKeys):
                        self.keyHeld(heldKeys)
            self.redrawGameWindow(screen)
        pygame.quit()

game = PygameGame()
game.run()

import { Component, OnInit, OnDestroy } from "@angular/core";
import { CommonModule } from "@angular/common";
import { NzGridModule } from "ng-zorro-antd/grid";
import { NzCardModule } from "ng-zorro-antd/card";
import { NzIconModule } from "ng-zorro-antd/icon";
import { DashboardStatsComponent } from "../dashboard-stats/dashboard-stats.component";

interface Effect {
    x: number;
    y: number;
    type: 'pole' | 'spark' | 'lightning' | 'fire';
    life: number;
    maxLife: number;
    char: string;
    color: string;
}

@Component({
  selector: "app-dashboard",
  templateUrl: "./dashboard.component.html",
  styleUrls: ["./dashboard.component.scss"],
  standalone: true,
  imports: [
    CommonModule,
    NzGridModule,
    NzCardModule,
    NzIconModule,
    DashboardStatsComponent
  ]
})
export class DashboardComponent implements OnInit, OnDestroy {
  private canvas!: HTMLCanvasElement;
  private context!: CanvasRenderingContext2D;
  private fontSize = 12;
  private effects: Effect[] = [];
  private animationFrameId?: number;
  private frameCount = 0;

  private poleChars = ['|', '║', '│', '┃', '┆', '┊'];
  private sparkChars = ['*', '✦', '✧', '✱', '✲', '✳', '⚡', '※'];
  private lightningChars = ['╱', '╲', '/', '\\', '⚡', '〰', '~', 'N', 'Z'];
  private fireChars = ['▲', '▼', '♦', '◆', '◊', '※', '*', '^', '~'];

  private fireColors = ['#FF4500', '#FF6347', '#FFD700', '#FFA500', '#FF8C00'];
  private lightningColors = ['#FFFFFF', '#E0E6FF', '#B0C4DE', '#87CEEB'];
  private sparkColors = ['#FFFF00', '#FFD700', '#FFF8DC', '#FFFACD'];
  private poleColors = ['#696969', '#708090', '#778899', '#2F4F4F'];

  ngOnInit() {
    setTimeout(() => this.initAnimation(), 100);
  }

  ngOnDestroy() {
    if (this.animationFrameId) {
      cancelAnimationFrame(this.animationFrameId);
    }
  }

  private initAnimation() {
    this.canvas = document.getElementById('matrixCanvas') as HTMLCanvasElement;
    if (!this.canvas) return;

    this.context = this.canvas.getContext('2d') as CanvasRenderingContext2D;
    this.canvas.width = this.canvas.offsetWidth;
    this.canvas.height = this.canvas.offsetHeight;

    this.createInitialPoles();
    this.animate();
  }

  private createInitialPoles() {
    const columns = Math.floor(this.canvas.width / (this.fontSize * 3));
    for (let i = 0; i < columns; i++) {
      const x = i * (this.fontSize * 3) + Math.random() * this.fontSize;
      const poleHeight = Math.floor(this.canvas.height / this.fontSize);
      
      for (let j = 0; j < poleHeight; j++) {
        if (Math.random() > 0.3) {
          this.effects.push({
            x: x,
            y: j * this.fontSize,
            type: 'pole',
            life: Infinity,
            maxLife: Infinity,
            char: this.poleChars[Math.floor(Math.random() * this.poleChars.length)],
            color: this.poleColors[Math.floor(Math.random() * this.poleColors.length)]
          });
        }
      }
    }
  }

  private createSpark() {
    this.effects.push({
      x: Math.random() * this.canvas.width,
      y: Math.random() * this.canvas.height,
      type: 'spark',
      life: 0,
      maxLife: 15 + Math.random() * 10,
      char: this.sparkChars[Math.floor(Math.random() * this.sparkChars.length)],
      color: this.sparkColors[Math.floor(Math.random() * this.sparkColors.length)]
    });
  }

  private createLightning() {
    const startX = Math.random() * this.canvas.width;
    const startY = 0;
    const segments = 8 + Math.random() * 12;
    
    let currentX = startX;
    let currentY = startY;
    
    for (let i = 0; i < segments; i++) {
      currentX += (Math.random() - 0.5) * 40;
      currentY += this.canvas.height / segments;
      
      this.effects.push({
        x: currentX,
        y: currentY,
        type: 'lightning',
        life: 0,
        maxLife: 8 + Math.random() * 5,
        char: this.lightningChars[Math.floor(Math.random() * this.lightningChars.length)],
        color: this.lightningColors[Math.floor(Math.random() * this.lightningColors.length)]
      });
    }
  }

  private createFire() {
    const baseX = Math.random() * this.canvas.width;
    const baseY = this.canvas.height - 20;
    const flameHeight = 60 + Math.random() * 40;
    
    for (let i = 0; i < 8; i++) {
      this.effects.push({
        x: baseX + (Math.random() - 0.5) * 30,
        y: baseY - Math.random() * flameHeight,
        type: 'fire',
        life: 0,
        maxLife: 20 + Math.random() * 15,
        char: this.fireChars[Math.floor(Math.random() * this.fireChars.length)],
        color: this.fireColors[Math.floor(Math.random() * this.fireColors.length)]
      });
    }
  }

  private animate() {
    this.context.fillStyle = 'rgba(0, 0, 0, 0.08)';
    this.context.fillRect(0, 0, this.canvas.width, this.canvas.height);

    this.context.font = this.fontSize + 'px monospace';

    // Create new effects randomly
    if (Math.random() < 0.3) this.createSpark();
    if (Math.random() < 0.05) this.createLightning();
    if (Math.random() < 0.08) this.createFire();

    // Update and render effects
    this.effects = this.effects.filter(effect => {
      if (effect.type !== 'pole') {
        effect.life++;
        if (effect.life > effect.maxLife) {
          return false;
        }
      }

      // Apply effect-specific behavior
      if (effect.type === 'fire') {
        effect.y -= 0.5 + Math.random();
        effect.x += (Math.random() - 0.5) * 2;
        const intensity = 1 - (effect.life / effect.maxLife);
        this.context.globalAlpha = intensity;
      } else if (effect.type === 'spark') {
        const intensity = Math.sin((effect.life / effect.maxLife) * Math.PI);
        this.context.globalAlpha = intensity;
      } else if (effect.type === 'lightning') {
        this.context.globalAlpha = Math.random() > 0.5 ? 1 : 0.3;
      } else {
        this.context.globalAlpha = 0.7;
      }

      this.context.fillStyle = effect.color;
      this.context.fillText(effect.char, effect.x, effect.y);

      return true;
    });

    this.context.globalAlpha = 1;
    this.frameCount++;
    this.animationFrameId = requestAnimationFrame(() => this.animate());
  }
}
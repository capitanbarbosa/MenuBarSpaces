"use client";

import { type CSSProperties, useState } from "react";
import styles from "../app/page.module.css";

const initialNames = ["Log", "dev", "biz", "kgp"];

const desktops = [
  {
    eyebrow: "Deep work",
    title: "Ship the feature.",
    detail: "Terminal, logs, and the signal you need.",
    color: "#ffb86b",
    glow: "#e96745",
  },
  {
    eyebrow: "Build",
    title: "Stay in flow.",
    detail: "Editor, preview, and docs—one Space away.",
    color: "#8be3c5",
    glow: "#29a886",
  },
  {
    eyebrow: "Business",
    title: "Keep context tidy.",
    detail: "Planning and numbers get a home of their own.",
    color: "#b8a5ff",
    glow: "#7058d7",
  },
  {
    eyebrow: "Playground",
    title: "Room to explore.",
    detail: "A clean desktop for everything experimental.",
    color: "#8fc9ff",
    glow: "#397ac7",
  },
];

export function MenuBarDemo() {
  const [names, setNames] = useState(initialNames);
  const [active, setActive] = useState(1);
  const [menuOpen, setMenuOpen] = useState(false);

  const desktop = desktops[active % desktops.length];

  function rename(index: number, value: string) {
    setNames((current) =>
      current.map((name, itemIndex) =>
        itemIndex === index ? value.slice(0, 20) : name,
      ),
    );
  }

  function addDemoSpace() {
    setNames((current) =>
      current.length >= 7 ? current : [...current, `${current.length + 1}`],
    );
  }

  function removeDemoSpace() {
    if (names.length <= 2) return;
    const nextLength = names.length - 1;
    setNames((current) => current.slice(0, nextLength));
    setActive((value) => Math.min(value, nextLength - 1));
  }

  return (
    <div className={styles.demoShell}>
      <div className={styles.demoTopline}>
        <span className={styles.liveDot} />
        Interactive preview
        <span className={styles.demoHint}>Try the menu bar</span>
      </div>

      <div
        className={styles.macDesktop}
        style={
          {
            "--desktop-color": desktop.color,
            "--desktop-glow": desktop.glow,
          } as CSSProperties
        }
      >
        <div className={styles.macMenuBar}>
          <div className={styles.macMenuLeft}>
            <span className={styles.appleGlyph}>●</span>
            <span>Finder</span>
            <span className={styles.macMenuWord}>File</span>
            <span className={styles.macMenuWord}>View</span>
          </div>

          <div className={styles.macMenuRight}>
            {names.map((name, index) => (
              <button
                className={`${styles.spaceButton} ${
                  active === index ? styles.spaceButtonActive : ""
                }`}
                key={`${index}-${name}`}
                onClick={() => {
                  setActive(index);
                  setMenuOpen(false);
                }}
                type="button"
                aria-label={`Switch to Desktop ${index + 1}: ${name || index + 1}`}
              >
                {active === index ? `[${name || index + 1}]` : name || index + 1}
              </button>
            ))}

            <div className={styles.spacesMenuWrap}>
              <button
                className={`${styles.spaceButton} ${styles.spacesTrigger}`}
                onClick={() => setMenuOpen((open) => !open)}
                type="button"
                aria-expanded={menuOpen}
              >
                Spaces
              </button>

              {menuOpen && (
                <div className={styles.spacesPopover}>
                  <div className={styles.popoverHeader}>
                    <div>
                      <strong>Space names</strong>
                      <span>{names.length} detected</span>
                    </div>
                    <span className={styles.statusPill}>Live</span>
                  </div>

                  <div className={styles.renameList}>
                    {names.map((name, index) => (
                      <label className={styles.renameRow} key={index}>
                        <span>{index + 1}</span>
                        <input
                          value={name}
                          onChange={(event) => rename(index, event.target.value)}
                          aria-label={`Rename Desktop ${index + 1}`}
                        />
                      </label>
                    ))}
                  </div>

                  <div className={styles.popoverActions}>
                    <button onClick={addDemoSpace} type="button">
                      + Demo Space
                    </button>
                    <button onClick={removeDemoSpace} type="button">
                      − Remove
                    </button>
                  </div>

                  <div className={styles.popoverStatus}>
                    <span className={styles.statusCheck}>✓</span>
                    Space API connected
                  </div>
                </div>
              )}
            </div>

            <span className={styles.statusIcon}>◒</span>
            <span className={styles.statusIcon}>⌁</span>
            <span className={styles.clock}>9:41</span>
          </div>
        </div>

        <div className={styles.desktopAmbientOne} />
        <div className={styles.desktopAmbientTwo} />

        <div className={styles.desktopCard}>
          <span>{desktop.eyebrow}</span>
          <h3>{desktop.title}</h3>
          <p>{desktop.detail}</p>
          <div className={styles.desktopCardMeta}>
            <span className={styles.windowDots}>
              <i />
              <i />
              <i />
            </span>
            Desktop {active + 1}
          </div>
        </div>
      </div>

      <div className={styles.demoFooter}>
        <span>Click a name to jump</span>
        <span>Open Spaces to rename</span>
        <span>Changes save automatically</span>
      </div>
    </div>
  );
}

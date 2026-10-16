import Image from "next/image";
import { MenuBarDemo } from "@/components/MenuBarDemo";
import styles from "./page.module.css";

const githubUrl =
  "https://github.com/capitanbarbosa/MenuBarSpaces";

const downloadUrl =
  process.env.NEXT_PUBLIC_DOWNLOAD_URL ??
  `${githubUrl}/releases/latest/download/MenuBarSpaces.zip`;

const features = [
  {
    number: "01",
    title: "Jump without breaking flow",
    text: "Every Desktop lives in your menu bar. One click takes you exactly where you meant to go.",
    icon: "↗",
  },
  {
    number: "02",
    title: "Names that mean something",
    text: "Turn Desktop 1, 2, and 3 into Log, dev, and biz—or whatever matches the way you work.",
    icon: "Aa",
  },
  {
    number: "03",
    title: "Always in sync",
    text: "Add or remove a Desktop in Mission Control and the menu updates automatically.",
    icon: "◎",
  },
  {
    number: "04",
    title: "Native and lightweight",
    text: "Built in Swift and AppKit. No browser shell, no account, and no background analytics.",
    icon: "⌘",
  },
];

const faqs = [
  {
    question: "macOS says MenuBarSpaces was not opened. Is the download broken?",
    answer:
      "No. The GitHub zip is unsigned, so Gatekeeper shows “MenuBarSpaces” Not Opened with only Move to Trash and Done. Click Done, then go to System Settings → Privacy & Security, scroll to the bottom, and click Open Anyway. If that button is missing, Control-click the app in Finder and choose Open.",
  },
  {
    question: "Why is Menu Bar Spaces distributed directly?",
    answer:
      "Mission Control does not expose public APIs for switching and enumerating Spaces. The current download is an unsigned zip from GitHub Releases so you can try it without the Apple Developer Program. A Developer ID signed and notarized build is the path that removes the first-open warning.",
  },
  {
    question: "Does it send any data anywhere?",
    answer:
      "No. Space names are stored locally in macOS preferences. The app has no account system, telemetry, or cloud service.",
  },
  {
    question: "Does it support new or deleted Spaces?",
    answer:
      "Yes. The menu tracks regular Mission Control Desktops and adds or removes buttons automatically.",
  },
  {
    question: "Will it launch when I sign in?",
    answer:
      "Yes. Add Menu Bar Spaces under System Settings → General → Login Items → Open at Login, and your Space controls will be ready with every Mac session.",
  },
];

export default function Home() {
  return (
    <div className={styles.page}>
      <header className={styles.navWrap}>
        <nav className={styles.nav} aria-label="Main navigation">
          <a className={styles.brand} href="#top" aria-label="Menu Bar Spaces home">
            <Image
              className={styles.brandMark}
              src="/logo.png"
              alt=""
              width={28}
              height={28}
            />
            Menu Bar Spaces
          </a>

          <div className={styles.navLinks}>
            <a href="#features">Features</a>
            <a href="#install">Install</a>
            <a href="#faq">FAQ</a>
          </div>

          <a
            className={styles.navGithub}
            href={githubUrl}
            target="_blank"
            rel="noreferrer"
          >
            GitHub
            <span aria-hidden="true">↗</span>
          </a>
        </nav>
      </header>

      <main>
        <section className={styles.hero} id="top">
          <div className={styles.heroGlow} />
          <div className={styles.heroGrid} />

          <div className={styles.heroContent}>
            <div className={styles.eyebrow}>
              <span className={styles.eyebrowDot} />
              Native menu bar Spaces switcher
            </div>

            <h1>
              Your Mac Spaces,
              <br />
              <span>one click away.</span>
            </h1>

            <p className={styles.heroCopy}>
              Name every Desktop. See the active one. Jump between them without
              gestures, shortcuts, or losing your train of thought.
            </p>

            <div className={styles.heroActions}>
              <a className={styles.primaryButton} href={downloadUrl}>
                <span className={styles.downloadIcon} aria-hidden="true">
                  ↓
                </span>
                Download for macOS
              </a>
              <a className={styles.secondaryButton} href="#demo">
                See how it works
                <span aria-hidden="true">↓</span>
              </a>
            </div>

            <div className={styles.heroMeta}>
              <span>macOS 13+</span>
              <i />
              <span>Apple Silicon + Intel</span>
              <i />
              <span>Free download</span>
            </div>
          </div>

          <div className={styles.heroDemo} id="demo">
            <MenuBarDemo />
          </div>
        </section>

        <section className={styles.signalStrip} aria-label="Product qualities">
          <div>
            <span>100%</span>
            Native Swift
          </div>
          <div>
            <span>0</span>
            Accounts
          </div>
          <div>
            <span>0</span>
            Trackers
          </div>
          <div>
            <span>∞</span>
            Context saved
          </div>
        </section>

        <section className={styles.featuresSection} id="features">
          <div className={styles.sectionIntro}>
            <span className={styles.sectionLabel}>Made for spatial thinkers</span>
            <h2>A tiny utility that keeps your whole workspace close.</h2>
            <p>
              Your Desktops are already organized. Menu Bar Spaces makes that
              organization visible and instantly reachable.
            </p>
          </div>

          <div className={styles.featureGrid}>
            {features.map((feature) => (
              <article className={styles.featureCard} key={feature.number}>
                <div className={styles.featureCardTop}>
                  <span className={styles.featureNumber}>{feature.number}</span>
                  <span className={styles.featureIcon}>{feature.icon}</span>
                </div>
                <h3>{feature.title}</h3>
                <p>{feature.text}</p>
              </article>
            ))}
          </div>
        </section>

        <section className={styles.workflowSection}>
          <div className={styles.workflowVisual}>
            <div className={styles.workflowNoise} />
            <span className={styles.workflowKicker}>A calmer way to navigate</span>
            <div className={styles.workflowMenu}>
              <span>[Log]</span>
              <span>dev</span>
              <span>biz</span>
              <span>kgp</span>
              <b>Spaces</b>
            </div>
            <div className={styles.workflowArrow}>→</div>
            <div className={styles.workflowWindow}>
              <div>
                <i />
                <i />
                <i />
              </div>
              <strong>Log</strong>
              <span>Desktop 1</span>
            </div>
          </div>

          <div className={styles.workflowCopy}>
            <span className={styles.sectionLabel}>Built around your flow</span>
            <h2>Mission Control, minus the mission.</h2>
            <p>
              No overview animation. No memorized keyboard combinations. Your
              named Spaces stay in the top menu bar, and the active one follows
              you when you swipe.
            </p>
            <ul>
              <li>
                <span>✓</span> Detects your real Desktop count
              </li>
              <li>
                <span>✓</span> Tracks gestures and Mission Control changes
              </li>
              <li>
                <span>✓</span> Saves custom names between restarts
              </li>
            </ul>
          </div>
        </section>

        <section className={styles.installSection} id="install">
          <div className={styles.installHeader}>
            <div>
              <span className={styles.sectionLabel}>Direct distribution</span>
              <h2>From download to flow in under a minute.</h2>
            </div>
            <div className={styles.trustBadge}>
              <span>!</span>
              First-open approval
              <small>Unsigned GitHub zip</small>
            </div>
          </div>

          <div className={styles.installSteps}>
            <article>
              <span className={styles.stepNumber}>1</span>
              <div className={styles.stepGraphic}>
                <div className={styles.dmgIcon}>↓</div>
              </div>
              <h3>Download the zip</h3>
              <p>Get the latest <code>MenuBarSpaces.zip</code> from GitHub Releases.</p>
            </article>
            <article>
              <span className={styles.stepNumber}>2</span>
              <div className={styles.stepGraphic}>
                <div className={styles.dragApp}>[ ]</div>
                <span className={styles.dragArrow}>→</span>
                <div className={styles.folderIcon}>A</div>
              </div>
              <h3>Move to Applications</h3>
              <p>Unzip, then drag <code>MenuBarSpaces.app</code> into Applications.</p>
            </article>
            <article>
              <span className={styles.stepNumber}>3</span>
              <div className={styles.stepGraphic}>
                <div className={styles.settingsGraphic}>
                  <span>Done</span>
                  <span>Open Anyway</span>
                </div>
              </div>
              <h3>Approve the first open</h3>
              <p>
                Double-click shows “Not Opened”. Click Done, then Open Anyway
                in System Settings.
              </p>
            </article>
            <article>
              <span className={styles.stepNumber}>4</span>
              <div className={styles.stepGraphic}>
                <div className={styles.launchGraphic}>
                  <span>[dev]</span>
                  <span>Spaces</span>
                </div>
              </div>
              <h3>Launch and name</h3>
              <p>Open Menu Bar Spaces, click Spaces, and make each Desktop yours.</p>
            </article>
          </div>

          <div className={styles.installNote}>
            <strong>If macOS says “MenuBarSpaces” Not Opened</strong>
            <ol>
              <li>Click <b>Done</b>. Do not move it to Trash.</li>
              <li>
                Open <b>System Settings → Privacy &amp; Security</b> and scroll
                to the bottom.
              </li>
              <li>
                Click <b>Open Anyway</b> next to MenuBarSpaces, then confirm{" "}
                <b>Open</b>.
              </li>
              <li>
                If Open Anyway is missing, Control-click the app in Finder and
                choose <b>Open</b>, then <b>Open</b> again.
              </li>
            </ol>
            <p>
              Later launches from Applications work normally. Each new
              downloaded version needs this once.
            </p>
          </div>

          <div className={styles.installCta}>
            <div>
              <strong>Menu Bar Spaces 0.1</strong>
              <span>Unsigned zip · macOS 13 or newer</span>
            </div>
            <a className={styles.primaryButton} href={downloadUrl}>
              Download .zip
              <span aria-hidden="true">↓</span>
            </a>
          </div>
        </section>

        <section className={styles.privacySection}>
          <div className={styles.privacyOrb}>
            <span>⌁</span>
          </div>
          <div>
            <span className={styles.sectionLabel}>Private by default</span>
            <h2>Your workspace stays on your Mac.</h2>
            <p>
              Menu Bar Spaces does one job locally. Names are stored in macOS
              preferences. There are no accounts, analytics SDKs, cloud sync,
              or data collection.
            </p>
          </div>
          <div className={styles.privacyFacts}>
            <span>
              <b>No</b> telemetry
            </span>
            <span>
              <b>No</b> sign-in
            </span>
            <span>
              <b>No</b> network service
            </span>
          </div>
        </section>

        <section className={styles.faqSection} id="faq">
          <div className={styles.sectionIntro}>
            <span className={styles.sectionLabel}>Questions, answered</span>
            <h2>The details before you download.</h2>
          </div>

          <div className={styles.faqList}>
            {faqs.map((faq) => (
              <details key={faq.question}>
                <summary>
                  {faq.question}
                  <span>+</span>
                </summary>
                <p>{faq.answer}</p>
              </details>
            ))}
          </div>
        </section>

        <section className={styles.finalCta}>
          <div className={styles.finalGlow} />
          <span className={styles.sectionLabel}>Less switching. More doing.</span>
          <h2>Give every Space a name—and every click a destination.</h2>
          <a className={styles.lightButton} href={downloadUrl}>
            Download Menu Bar Spaces
            <span>↓</span>
          </a>
          <p>macOS 13+ · Universal · Free</p>
        </section>
      </main>

      <footer className={styles.footer}>
        <a className={styles.brand} href="#top">
          <Image
            className={styles.brandMark}
            src="/logo.png"
            alt=""
            width={28}
            height={28}
          />
          Menu Bar Spaces
        </a>
        <p>Built for people with more than one thing going on.</p>
        <div>
          <a href={githubUrl} target="_blank" rel="noreferrer">
            GitHub
          </a>
          <a href="#install">Download</a>
          <a href="#faq">FAQ</a>
        </div>
      </footer>
    </div>
  );
}

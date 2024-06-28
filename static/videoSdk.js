function _objectWithoutPropertiesLoose(e, a) {
    if (null == e) return {};
    var t, o, n = {},
      r = Object.keys(e);
    for (o = 0; o < r.length; o++) t = r[o], a.indexOf(t) >= 0 || (n[t] = e[t]);
    return n;
  }
  var _excluded = ["containerId"],
    VideoSDKMeeting = function () {
      function e() {}
      var a = e.prototype;
      return a.init = function (e) {
        var a = void 0 === e ? {} : e,
          t = a.containerId,
          o = _objectWithoutPropertiesLoose(a, _excluded);
        try {
          var n = parent.document,
            r = parent.window;
          if (void 0 === r || void 0 === n) throw new Error("No browser detected!");
          return Promise.resolve(this.generatePrebuiltSrc(o, r, n)).then(function (e) {
            var a = n.createElement("iframe");
            a.id = "videosdk-frame", a.src = e, a.allowfullscreen = !0, a.width = "100%", a.height = "100%", a.allow = "camera *; microphone *; fullscreen; display-capture; allow-same-origin; allow-presentation; encrypted-media; midi; encrypted-media ", a.style.border = 0, a.allowusermedia = "allowusermedia";
            var o = null;
            if (t) {
              var l = n.getElementById(t);
              if (!l) throw new Error("No Container found with id " + t);
              o = l, l.appendChild(a);
            } else {
              var i = n.createElement("div");
              i.style.position = "fixed", i.style.left = 0, i.style.right = 0, i.style.bottom = 0, i.style.top = 0, o = i, i.appendChild(a), n.body.style.margin = "0px", n.body.style.padding = "0px", n.body.style.height = "100%", n.body.style.overflow = "hidden", n.body.appendChild(i);
            }
            r.addEventListener("popstate", function (e) {
              o.remove();
            });
          });
        } catch (e) {
          return Promise.reject(e);
        }
      }, a.fetchToken = function (e) {
        var a = e.apiKey,
          t = e.askJoin,
          o = e.participantCanToggleOtherWebcam,
          n = e.participantCanToggleOtherMic,
          r = e.partcipantCanToogleOtherScreenShare,
          l = e.apiBaseUrl;
        try {
          var i = (l || "https://api.videosdk.live") + "/v1/prebuilt/token",
            u = [];
          t ? u.push("ask_join") : u.push("allow_join"), o || n || r ? u.push("allow_mod") : u.push("allow_join");
          var s = {
            apiKey: a
          };
          return u.length && (s.permissions = u), Promise.resolve(fetch(i, {
            method: "POST",
            headers: {
              "Content-type": "application/json"
            },
            body: JSON.stringify(s)
          })).then(function (e) {
            var a, t = function () {
              if (200 === e.status) return Promise.resolve(e.json()).then(function (e) {
                a = e.token;
              });
              throw new Error("Could not fetch token.");
            }();
            return t && t.then ? t.then(function (e) {
              return a;
            }) : a;
          });
        } catch (e) {
          return Promise.reject(e);
        }
      }, a.generatePrebuiltSrc = function (e, a) {
        var t = void 0 === e ? {} : e,
          o = t.name,
          n = t.apiKey,
          r = t.meetingId,
          l = t.token,
          i = t.region,
          u = t.preferredProtocol,
          s = t.redirectOnLeave,
          c = t.micEnabled,
          y = t.webcamEnabled,
          d = t.participantCanToggleSelfWebcam,
          p = t.participantCanToggleSelfMic,
          v = t.participantTabPanelEnabled,
          f = t.moreOptionsEnabled,
          b = t.participantCanLeave,
          g = t.chatEnabled,
          k = t.screenShareEnabled,
          h = t.pollEnabled,
          m = t.whiteboardEnabled,
          S = t.raiseHandEnabled,
          E = t.theme,
          w = t.branding,
          T = t.livestream,
          C = t.recording,
          P = t.hls,
          L = t.waitingScreen,
          O = t.permissions,
          j = t.joinScreen,
          U = t.leftScreen,
          M = t.layout,
          R = t.maxResolution,
          A = t.debug,
          B = t.isRecorder,
          W = t.videoConfig,
          I = t.screenShareConfig,
          _ = t.audioConfig,
          x = t.i18n,
          D = t.maintainVideoAspectRatio,
          V = t.maintainLandscapeVideoAspectRatio,
          z = t.networkBarEnabled,
          K = t.participantId,
          H = t.meetingLayoutTopic,
          J = t.joinWithoutUserInteraction,
          N = t.notificationSoundEnabled,
          F = t.notificationAlertsEnabled,
          q = t.animationsEnabled,
          G = t.topbarEnabled,
          Q = t.hideLocalParticipant,
          Y = t.alwaysShowOverlay,
          X = t.sideStackSize,
          Z = t.reduceEdgeSpacing,
          $ = t.embedBaseUrl,
          ee = t.apiBaseUrl,
          ae = t.mode;
        try {
          var te = function (e) {
            var t;
            l = e;
            var n = null == a || null === (t = a.navigator) || void 0 === t ? void 0 : t.userAgent,
              w = [{
                key: "micEnabled",
                value: c ? "true" : "false"
              }, {
                key: "webcamEnabled",
                value: y ? "true" : "false"
              }, {
                key: "name",
                value: o
              }, {
                key: "meetingId",
                value: r || ""
              }, {
                key: "region",
                value: i || "sg001"
              }, {
                key: "preferredProtocol",
                value: u || "UDP_ONLY"
              }, {
                key: "canChangeLayout",
                value: ke ? "true" : "false"
              }, {
                key: "redirectOnLeave",
                value: s || ""
              }, {
                key: "chatEnabled",
                value: g ? "true" : "false"
              }, {
                key: "theme",
                value: E || "DEFAULT"
              }, {
                key: "language",
                value: pa || "en"
              }, {
                key: "screenShareEnabled",
                value: k ? "true" : "false"
              }, {
                key: "pollEnabled",
                value: "boolean" == typeof h ? h ? "true" : "false" : "true"
              }, {
                key: "whiteboardEnabled",
                value: m ? "true" : "false"
              }, {
                key: "participantCanToggleSelfWebcam",
                value: d ? "true" : "false"
              }, {
                key: "participantCanToggleSelfMic",
                value: p ? "true" : "false"
              }, {
                key: "raiseHandEnabled",
                value: S ? "true" : "false"
              }, {
                key: "token",
                value: l || ""
              }, {
                key: "recordingEnabled",
                value: Je ? "true" : "false"
              }, {
                key: "recordingWebhookUrl",
                value: Ne || ""
              }, {
                key: "recordingAWSDirPath",
                value: Fe || ""
              }, {
                key: "autoStartRecording",
                value: qe ? "true" : "false"
              }, {
                key: "recordingTheme",
                value: Ge || "DEFAULT"
              }, {
                key: "participantCanToggleRecording",
                value: "boolean" == typeof ve && (ve ? "true" : "false")
              }, {
                key: "brandingEnabled",
                value: aa ? "true" : "false"
              }, {
                key: "brandLogoURL",
                value: ta || ""
              }, {
                key: "brandName",
                value: oa
              }, {
                key: "participantCanLeave",
                value: "boolean" == typeof b ? b ? "true" : "false" : "true"
              }, {
                key: "poweredBy",
                value: "boolean" == typeof na ? na ? "true" : "false" : "true"
              }, {
                key: "liveStreamEnabled",
                value: Ee ? "true" : "false"
              }, {
                key: "autoStartLiveStream",
                value: we ? "true" : "false"
              }, {
                key: "liveStreamOutputs",
                value: JSON.stringify(Te || [])
              }, {
                key: "liveStreamTheme",
                value: Ce || "DEFAULT"
              }, {
                key: "participantCanToggleOtherMic",
                value: le ? "true" : "false"
              }, {
                key: "participantTabPanelEnabled",
                value: "boolean" == typeof v ? v ? "true" : "false" : "true"
              }, {
                key: "moreOptionsEnabled",
                value: "boolean" == typeof f ? f ? "true" : "false" : "true"
              }, {
                key: "partcipantCanToogleOtherScreenShare",
                value: ie ? "true" : "false"
              }, {
                key: "participantCanToggleOtherWebcam",
                value: re ? "true" : "false"
              }, {
                key: "participantCanToggleOtherMode",
                value: ue ? "true" : "false"
              }, {
                key: "askJoin",
                value: ne ? "true" : "false"
              }, {
                key: "joinScreenEnabled",
                value: Ue ? "true" : "false"
              }, {
                key: "joinScreenMeetingUrl",
                value: Me || ""
              }, {
                key: "joinScreenTitle",
                value: Re || ""
              }, {
                key: "notificationSoundEnabled",
                value: "boolean" == typeof N ? N ? "true" : "false" : "true"
              }, {
                key: "canPin",
                value: ge ? "true" : "false"
              }, {
                key: "canCreatePoll",
                value: he ? "true" : "false"
              }, {
                key: "canToggleParticipantTab",
                value: "boolean" == typeof me ? me ? "true" : "false" : "true"
              }, {
                key: "layoutType",
                value: Ve
              }, {
                key: "mode",
                value: ae
              }, {
                key: "participantCanEndMeeting",
                value: "boolean" == typeof ce && ce ? "true" : "false"
              }, {
                key: "canDrawOnWhiteboard",
                value: "boolean" == typeof ye ? ye ? "true" : "false" : "true"
              }, {
                key: "canToggleWhiteboard",
                value: "boolean" == typeof de ? de ? "true" : "false" : "true"
              }, {
                key: "canToggleVirtualBackground",
                value: "boolean" == typeof pe ? pe ? "true" : "false" : "true"
              }, {
                key: "canRemoveOtherParticipant",
                value: "boolean" == typeof se && se ? "true" : "false"
              }, {
                key: "leftScreenActionButtonLabel",
                value: _e
              }, {
                key: "leftScreenActionButtonHref",
                value: xe
              }, {
                key: "maxResolution",
                value: R || "sd"
              }, {
                key: "animationsEnabled",
                value: "boolean" != typeof q || q
              }, {
                key: "topbarEnabled",
                value: "boolean" != typeof G || G
              }, {
                key: "notificationAlertsEnabled",
                value: "boolean" != typeof F || F
              }, {
                key: "debug",
                value: "boolean" == typeof A && A
              }, {
                key: "participantId",
                value: K || ""
              }, {
                key: "layoutPriority",
                value: ze || ""
              }, {
                key: "layoutGridSize",
                value: Ke || "0"
              }, {
                key: "hideLocalParticipant",
                value: "boolean" == typeof Q && Q ? "true" : "false"
              }, {
                key: "alwaysShowOverlay",
                value: "boolean" == typeof Y && Y ? "true" : "false"
              }, {
                key: "sideStackSize",
                value: X
              }, {
                key: "reduceEdgeSpacing",
                value: "boolean" == typeof Z && Z ? "true" : "false"
              }, {
                key: "isRecorder",
                value: "boolean" == typeof B && B ? "true" : "false"
              }, {
                key: "maintainVideoAspectRatio",
                value: "boolean" == typeof D ? D ? "true" : "false" : "true"
              }, {
                key: "maintainLandscapeVideoAspectRatio",
                value: "boolean" == typeof V && V ? "true" : "false"
              }, {
                key: "networkBarEnabled",
                value: "boolean" == typeof z ? z ? "true" : "false" : "true"
              }, {
                key: "leftScreenRejoinButtonEnabled",
                value: "boolean" == typeof We ? We ? "true" : "false" : "true"
              }, {
                key: "joinWithoutUserInteraction",
                value: "boolean" == typeof J && J ? "true" : "false"
              }, {
                key: "rawUserAgent",
                value: n || ""
              }, {
                key: "meetingLayoutTopic",
                value: H || ""
              }, {
                key: "canChangeLayout",
                value: "boolean" == typeof ke && ke ? "true" : "false"
              }, {
                key: "participantCanToggleLivestream",
                value: "boolean" == typeof fe && fe ? "true" : "false"
              }, {
                key: "hlsEnabled",
                value: Ye ? "true" : "false"
              }, {
                key: "autoStartHls",
                value: Xe ? "true" : "false"
              }, {
                key: "participantCanToggleHls",
                value: "boolean" == typeof be && be ? "true" : "false"
              }, {
                key: "hlsPlayerControlsVisible",
                value: "boolean" == typeof Ze && Ze ? "true" : "false"
              }, {
                key: "hlsTheme",
                value: $e || "DEFAULT"
              }, {
                key: "waitingScreenImageUrl",
                value: Le || ""
              }, {
                key: "waitingScreenText",
                value: Oe || ""
              }, {
                key: "cameraResolution",
                value: ia || "h360p_w640p"
              }, {
                key: "cameraId",
                value: la || ""
              }, {
                key: "cameraOptimizationMode",
                value: ua || "motion"
              }, {
                key: "cameraMultiStream",
                value: "boolean" == typeof sa ? sa ? "true" : "false" : "true"
              }, {
                key: "screenShareResolution",
                value: ya || "h720p_15fps"
              }, {
                key: "screenShareOptimizationMode",
                value: da || "motion"
              }, {
                key: "micQuality",
                value: va || "speech_standard"
              }].map(function (e) {
                var a = e.key,
                  t = e.value;
                return a + "=" + encodeURIComponent(t);
              }).join("&");
            return ($ || "https://embed.videosdk.live/rtc-js-prebuilt/0.3.38/") + "/?" + w;
          };
          T || (T = {}), O || (O = {}), j || (j = {}), U || (U = {}), M || (M = {}), C || (C = {}), P || (P = {}), L || (L = {}), w || (w = {}), W || (W = {}), I || (I = {}), _ || (_ = {}), x || (x = {});
          var oe = O,
            ne = oe.askToJoin,
            re = oe.toggleParticipantWebcam,
            le = oe.toggleParticipantMic,
            ie = oe.toggleParticipantScreenshare,
            ue = oe.toggleParticipantMode,
            se = oe.removeParticipant,
            ce = oe.endMeeting,
            ye = oe.drawOnWhiteboard,
            de = oe.toggleWhiteboard,
            pe = oe.toggleVirtualBackground,
            ve = oe.toggleRecording,
            fe = oe.toggleLivestream,
            be = oe.toggleHls,
            ge = oe.pin,
            ke = oe.changeLayout,
            he = oe.canCreatePoll,
            me = oe.canToggleParticipantTab;
          ne && (re = !1, le = !1, ie = !1);
          var Se = T,
            Ee = Se.enabled,
            we = Se.autoStart,
            Te = Se.outputs,
            Ce = Se.theme,
            Pe = L,
            Le = Pe.imageUrl,
            Oe = Pe.text,
            je = j,
            Ue = je.visible,
            Me = je.meetingUrl,
            Re = je.title,
            Ae = U,
            Be = Ae.actionButton,
            We = Ae.rejoinButtonEnabled,
            Ie = Be = Be || {},
            _e = Ie.label,
            xe = Ie.href,
            De = M,
            Ve = De.type,
            ze = De.priority,
            Ke = De.gridSize,
            He = C,
            Je = He.enabled,
            Ne = He.webhookUrl,
            Fe = He.awsDirPath,
            qe = He.autoStart,
            Ge = He.theme,
            Qe = P,
            Ye = Qe.enabled,
            Xe = Qe.autoStart,
            Ze = Qe.playerControlsVisible,
            $e = Qe.theme,
            ea = w,
            aa = ea.enabled,
            ta = ea.logoURL,
            oa = ea.name,
            na = ea.poweredBy,
            ra = W,
            la = ra.cameraId,
            ia = ra.resolution,
            ua = ra.optimizationMode,
            sa = ra.multiStream,
            ca = I,
            ya = ca.resolution,
            da = ca.optimizationMode,
            pa = x.lang,
            va = _.quality;
          if (!l && !n) throw new Error('Any one of "token" or "apiKey" must be provided.');
          var fa = l;
          return Promise.resolve(fa ? te(fa) : Promise.resolve(this.fetchToken({
            apiKey: n,
            askJoin: ne,
            participantCanToggleOtherWebcam: re,
            participantCanToggleOtherMic: le,
            partcipantCanToogleOtherScreenShare: ie,
            apiBaseUrl: ee
          })).then(te));
        } catch (e) {
          return Promise.reject(e);
        }
      }, e
    }();
  
/**
 * Copyright (c) 2022, RTE (http://www.rte-france.com)
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/.
 */
package com.powsybl.benchmark;

import com.powsybl.ieeecdf.converter.IeeeCdfNetworkFactory;
import com.powsybl.iidm.network.Network;
import org.openjdk.jmh.annotations.Level;
import org.openjdk.jmh.annotations.Scope;
import org.openjdk.jmh.annotations.Setup;
import org.openjdk.jmh.annotations.State;

/**
 * @author Geoffroy Jamgotchian <geoffroy.jamgotchian at rte-france.com>
 */
@State(Scope.Thread)
public class IeeeNetworkState {

    private Network ieee14Network;

    private Network ieee118Network;

    private Network ieee300Network;

    @Setup(Level.Trial)
    public void doSetup() {
        ieee14Network = IeeeCdfNetworkFactory.create14();
        ieee118Network = IeeeCdfNetworkFactory.create118();
        ieee300Network = IeeeCdfNetworkFactory.create300();
    }

    public Network getIeee14Network() {
        return ieee14Network;
    }

    public Network getIeee118Network() {
        return ieee118Network;
    }

    public Network getIeee300Network() {
        return ieee300Network;
    }
}
